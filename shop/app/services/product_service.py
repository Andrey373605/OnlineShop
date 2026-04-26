import json
import logging
from dataclasses import asdict

from shop.app.core.ports.storage import StoragePort
from shop.app.models.domain.product import Product
from shop.app.models.domain.upload_source import UploadSource
from shop.app.models.schemas import (
    ProductCreate,
    ProductUpdate,
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
        storage: StoragePort,
        cache_ttl_seconds: int | None = None,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._pubsub = pubsub
        self._storage = storage
        self._cache_ttl_seconds = cache_ttl_seconds
        self._cache_pattern = "products:limit:*"

    async def create_product(self, data: ProductCreate, source: UploadSource) -> Product:
        async with self._uow as uow:
            product_data = data.model_dump()
            product_data["thumbnail_key"] = await self._storage.upload(source)

            product = await uow.products.create(product_data)
            await uow.commit()

        await self._after_mutation(product.id, "create")
        return product

    async def get_product_by_id(self, product_id: int) -> Product:
        async with self._uow as uow:
            product = await uow.products.get_by_id(product_id)
            return product

    async def get_all_products(self, limit: int, offset: int) -> list[Product]:
        key = f"products:limit:{limit}:offset:{offset}"
        if await self._cache.exists(key):
            items_str = await self._cache.get_list(key)
            return [Product(**json.loads(s)) for s in items_str]

        async with self._uow as uow:
            products = await uow.products.get_all(limit=limit, offset=offset)

        items_str = [json.dumps(asdict(p)) for p in products]
        await self._cache.set_list_atomic(key, items_str, ttl_seconds=self._cache_ttl_seconds)
        return products

    async def update_product(
        self, product_id: int, data: ProductUpdate, source: UploadSource | None
    ) -> Product:
        async with self._uow as uow:
            product = await uow.products.get_by_id(product_id)
            old_thumbnail_key = product.thumbnail_key

            update_data = data.model_dump(exclude_unset=True)

            if source is not None:
                new_thumbnail_key = await self._storage.upload(source)
                update_data["thumbnail_key"] = new_thumbnail_key

            updated_product = await uow.products.update(product_id, update_data)
            await uow.commit()

        if new_thumbnail_key is not None and old_thumbnail_key:
            await self._delete_storage_object_best_effort(old_thumbnail_key)

        return updated_product

    async def delete_product(self, product_id: int) -> None:
        async with self._uow as uow:
            product = await uow.products.get_by_id(product_id)
            await uow.products.delete(product_id)
            await uow.commit()

        await self._delete_storage_object_best_effort(product.thumbnail_key)
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

    async def _delete_orphan_thumbnail(self, thumbnail_key: str) -> None:
        try:
            await self._storage.delete(thumbnail_key)
        except Exception:
            logger.warning("Failed to delete orphan thumbnail: %s", thumbnail_key)

    async def _delete_storage_object_best_effort(self, thumbnail_key: str) -> None:
        try:
            await self._storage.delete(thumbnail_key)
        except Exception:
            logger.warning("Failed to delete product object: %s", thumbnail_key)
