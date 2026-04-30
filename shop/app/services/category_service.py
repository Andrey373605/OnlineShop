import json
import logging
from dataclasses import asdict

from shop.app.core.exceptions import (
    ApplicationUnavailableError,
    ConflictError,
    EntityNotFoundError,
)
from shop.app.models.domain.category import Category, CategoryCreateData, CategoryUpdateData
from shop.app.models.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
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

CATEGORIES_CACHE_KEY = "categories:all"
logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        pubsub: PubSubService,
        cache_ttl_seconds: int | None = None,
    ):
        self._uow = uow
        self._cache = cache
        self._pubsub = pubsub
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        category_data = CategoryCreateData.from_input(data)
        async with self._uow as uow:
            try:
                category = await uow.categories.create(category_data)
                await uow.commit()
            except RepositoryUniqueConstraintError as exc:
                raise ConflictError("Category already exists", details={"name": data.name}) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to create category") from exc

        await self._after_mutation(category.id, "create")
        return CategoryResponse(id=category.id, message="Category created successfully")

    async def get_category_by_id(self, category_id: int) -> Category:
        async with self._uow as uow:
            try:
                return await uow.categories.get_by_id(category_id)
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Category not found",
                    details={"category_id": category_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to fetch category") from exc

    async def get_all_categories(self) -> list[Category]:
        if await self._cache.exists(CATEGORIES_CACHE_KEY):
            try:
                items_str = await self._cache.get_list(CATEGORIES_CACHE_KEY)
                return [Category(**json.loads(s)) for s in items_str]
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                logger.warning(
                    "Category list cache corrupt, refetching: %s",
                    CATEGORIES_CACHE_KEY,
                    exc_info=True,
                )

        async with self._uow as uow:
            try:
                categories = await uow.categories.get_all()
            except RepositoryUnavailableError as exc:
                raise ApplicationUnavailableError("Failed to fetch categories") from exc
            except RepositoryMappingError as exc:
                raise ApplicationUnavailableError("Failed to map categories") from exc

        try:
            items_str = [json.dumps(asdict(c)) for c in categories]
            await self._cache.set_list_atomic(
                CATEGORIES_CACHE_KEY, items_str, ttl_seconds=self._cache_ttl_seconds
            )
        except Exception:
            logger.warning(
                "Failed to write category list cache: %s",
                CATEGORIES_CACHE_KEY,
                exc_info=True,
            )
        return categories

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        async with self._uow as uow:
            update_data = CategoryUpdateData(**data.model_dump(exclude_unset=True))
            try:
                category = await uow.categories.update(category_id, update_data)
                await uow.commit()
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Category not found",
                    details={"category_id": category_id},
                ) from exc
            except RepositoryUniqueConstraintError as exc:
                raise ConflictError("Category already exists", details={"category_id": category_id}) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to update category") from exc

        await self._after_mutation(category.id, "update")
        return CategoryResponse(id=category.id, message="Category updated successfully")

    async def delete_category(self, category_id: int) -> CategoryResponse:
        async with self._uow as uow:
            try:
                deleted = await uow.categories.delete(category_id)
                await uow.commit()
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Category not found",
                    details={"category_id": category_id},
                ) from exc
            except RepositoryForeignKeyError as exc:
                raise ConflictError(
                    "Category is referenced by another entity",
                    details={"category_id": category_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to delete category") from exc

        await self._after_mutation(deleted.id, "delete")
        return CategoryResponse(id=deleted.id, message="Category deleted successfully")

    async def category_id_exists(self, category_id: int) -> bool:
        async with self._uow as uow:
            return await uow.categories.exists_category_with_id(category_id)

    async def _invalidate_cache(self) -> None:
        await self._cache.delete(CATEGORIES_CACHE_KEY)

    async def _after_mutation(self, entity_id: int, action: str) -> None:
        await self._invalidate_cache()

        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "categories", "key": CATEGORIES_CACHE_KEY},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "categories", "action": action, "entity_id": entity_id},
        )
