import json
import logging
from dataclasses import asdict
from decimal import Decimal

from shop.app.core.exceptions import (
    ApplicationUnavailableError,
    ConflictError,
    DomainValidationError,
    EntityNotFoundError,
    StorageUnavailableError,
    StorageValidationError,
)
from shop.app.core.ports.file_storage import FileStoragePort
from shop.app.models.domain.product import (
    Product,
    ProductCreateData,
    ProductUpdateData,
)
from shop.app.models.domain.upload_source import UploadSource
from shop.app.models.schemas import (
    ProductCreate,
    ProductUpdate,
)
from shop.app.repositories.exceptions import (
    RepositoryForeignKeyError,
    RepositoryMappingError,
    RepositoryRecordNotFoundError,
    RepositoryUnavailableError,
    RepositoryUnexpectedResultError,
    RepositoryUniqueConstraintError,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.cache_service import CacheService
from shop.app.services.pubsub_service import PubSubChannel, PubSubService

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        pubsub: PubSubService,
        storage: FileStoragePort,
        cache_ttl_seconds: int | None = None,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._pubsub = pubsub
        self._storage = storage
        self._cache_ttl_seconds = cache_ttl_seconds
        self._cache_pattern = "products:limit:*"

    async def create_product(self, data: ProductCreate, source: UploadSource) -> Product:
        try:
            thumbnail_key = await self._storage.upload(source)
        except StorageValidationError as exc:
            raise DomainValidationError("Invalid product thumbnail file") from exc
        except StorageUnavailableError as exc:
            raise ApplicationUnavailableError("Product storage is unavailable") from exc

        try:
            async with self._uow as uow:
                product_data = ProductCreateData.from_input(
                    data=data,
                    thumbnail_key=thumbnail_key,
                )
                product = await uow.products.create(product_data)
                await uow.commit()
        except RepositoryForeignKeyError as exc:
            await self._delete_orphan_object(thumbnail_key)
            raise EntityNotFoundError(
                "Category not found",
                details={"category_id": data.category_id},
            ) from exc
        except RepositoryUniqueConstraintError as exc:
            await self._delete_orphan_object(thumbnail_key)
            raise ConflictError(
                "Product violates a unique constraint",
                details={"category_id": data.category_id},
            ) from exc
        except (
            RepositoryUnavailableError,
            RepositoryMappingError,
            RepositoryUnexpectedResultError,
        ) as exc:
            await self._delete_orphan_object(thumbnail_key)
            raise ApplicationUnavailableError("Failed to create product") from exc

        await self._after_mutation(product.id, "create")
        return product

    async def get_product_by_id(self, product_id: int) -> Product:
        async with self._uow as uow:
            try:
                return await uow.products.get_by_id(product_id)
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Product not found",
                    details={"product_id": product_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to fetch product") from exc

    async def get_all_products(self, limit: int, offset: int) -> list[Product]:
        key = f"products:limit:{limit}:offset:{offset}"
        if await self._cache.exists(key):
            try:
                items_str = await self._cache.get_list(key)
                return [self._product_from_cache_json(s) for s in items_str]
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                logger.warning(
                    "Product list cache corrupt, refetching: %s",
                    key,
                    exc_info=True,
                )

        async with self._uow as uow:
            try:
                products = await uow.products.get_all(limit=limit, offset=offset)
            except RepositoryUnavailableError as exc:
                raise ApplicationUnavailableError("Failed to fetch products") from exc
            except RepositoryMappingError as exc:
                raise ApplicationUnavailableError("Failed to map products") from exc

        try:
            items_str = [self._product_to_cache_json(p) for p in products]
            await self._cache.set_list_atomic(key, items_str, ttl_seconds=self._cache_ttl_seconds)
        except Exception:
            logger.warning("Failed to write product list cache: %s", key, exc_info=True)

        return products

    async def update_product(
        self, product_id: int, data: ProductUpdate, source: UploadSource | None
    ) -> Product:
        new_thumbnail_key: str | None = None
        if source is not None:
            try:
                new_thumbnail_key = await self._storage.upload(source)
            except StorageValidationError as exc:
                raise DomainValidationError("Invalid product thumbnail file") from exc
            except StorageUnavailableError as exc:
                raise ApplicationUnavailableError("Product storage is unavailable") from exc

        async with self._uow as uow:
            try:
                product = await uow.products.get_by_id(product_id)
            except RepositoryRecordNotFoundError as exc:
                await self._cleanup_new_thumbnail_if_any(new_thumbnail_key)
                raise EntityNotFoundError(
                    "Product not found",
                    details={"product_id": product_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                await self._cleanup_new_thumbnail_if_any(new_thumbnail_key)
                raise ApplicationUnavailableError("Failed to fetch product") from exc

            old_thumbnail_key = product.thumbnail_key

            fields = data.model_dump(exclude_unset=True)
            if new_thumbnail_key is not None:
                fields["thumbnail_key"] = new_thumbnail_key
            update_data = ProductUpdateData(**fields)

            try:
                updated_product = await uow.products.update(product_id, update_data)
                await uow.commit()
            except RepositoryRecordNotFoundError as exc:
                await self._cleanup_new_thumbnail_if_any(new_thumbnail_key)
                raise EntityNotFoundError(
                    "Product not found",
                    details={"product_id": product_id},
                ) from exc
            except RepositoryForeignKeyError as exc:
                await self._cleanup_new_thumbnail_if_any(new_thumbnail_key)
                raise EntityNotFoundError(
                    "Category not found",
                    details={"category_id": update_data.category_id},
                ) from exc
            except RepositoryUniqueConstraintError as exc:
                await self._cleanup_new_thumbnail_if_any(new_thumbnail_key)
                raise ConflictError(
                    "Product violates a unique constraint",
                    details={"product_id": product_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                await self._cleanup_new_thumbnail_if_any(new_thumbnail_key)
                raise ApplicationUnavailableError("Failed to update product") from exc

        if new_thumbnail_key is not None and old_thumbnail_key:
            await self._delete_storage_object_best_effort(old_thumbnail_key)

        return updated_product

    async def delete_product(self, product_id: int) -> None:
        async with self._uow as uow:
            try:
                deleted = await uow.products.delete(product_id)
                await uow.commit()
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Product not found",
                    details={"product_id": product_id},
                ) from exc
            except RepositoryForeignKeyError as exc:
                raise ConflictError(
                    "Product is referenced by another entity",
                    details={"product_id": product_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to delete product") from exc

        if deleted.thumbnail_key:
            await self._delete_storage_object_best_effort(deleted.thumbnail_key)
        await self._after_mutation(product_id, "delete")

    async def _after_mutation(self, entity_id: int, action: str) -> None:
        await self._cache.delete_by_pattern(self._cache_pattern)
        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "products", "pattern": self._cache_pattern},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "products", "action": action, "entity_id": entity_id},
        )

    async def _cleanup_new_thumbnail_if_any(self, thumbnail_key: str | None) -> None:
        if thumbnail_key is not None:
            await self._delete_orphan_object(thumbnail_key)

    async def _delete_orphan_object(self, thumbnail_key: str) -> None:
        try:
            await self._storage.delete(thumbnail_key)
        except Exception:
            logger.warning(
                "Failed to delete orphan product thumbnail: %s",
                thumbnail_key,
                exc_info=True,
            )

    async def _delete_storage_object_best_effort(self, thumbnail_key: str) -> None:
        try:
            await self._storage.delete(thumbnail_key)
        except Exception:
            logger.warning(
                "Failed to delete product thumbnail object: %s",
                thumbnail_key,
                exc_info=True,
            )

    @staticmethod
    def _product_to_cache_json(p: Product) -> str:
        payload = asdict(p)
        payload["price"] = str(payload["price"])
        return json.dumps(payload)

    @staticmethod
    def _product_from_cache_json(raw: str) -> Product:
        payload = json.loads(raw)
        payload["price"] = Decimal(str(payload["price"]))
        return Product(**payload)
