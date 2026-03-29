from shop.app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.schemas.category_schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryResponse,
    CategoryUpdate,
)
from shop.app.services.cache_service import CacheService
from shop.app.services.pubsub_service import PubSubChannel, PubSubService

CATEGORIES_CACHE_KEY = "categories:all"


class CategoryService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        pubsub: PubSubService,
        cache_ttl_seconds: int | None = None,
    ):
        self.uow = uow
        self.cache = cache
        self.pubsub = pubsub
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_category(self, data: CategoryCreate) -> dict:
        async with self.uow as uow:
            if await uow.categories.exists_category_with_name(data.name):
                raise AlreadyExistsError("Category name")

            category_id = await uow.categories.create(data.model_dump())
            if not category_id:
                raise OperationFailedError("Failed to create category")
            await uow.commit()

        await self._invalidate_cache()
        await self.pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "categories", "key": CATEGORIES_CACHE_KEY},
        )
        await self.pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "categories", "action": "create", "entity_id": category_id},
        )
        return {"id": category_id, "message": "Category created successfully"}

    async def get_category_by_id(self, category_id: int) -> CategoryOut:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(category_id)
            if not category:
                raise NotFoundError("Category")
            return category

    async def get_all_categories(self) -> list[CategoryOut]:
        if await self.cache.exists(CATEGORIES_CACHE_KEY):
            items_str = await self.cache.get_list(CATEGORIES_CACHE_KEY)
            return [CategoryOut.model_validate_json(s) for s in items_str]

        async with self.uow as uow:
            categories = await uow.categories.get_all()

        items_str = [c.model_dump_json() for c in categories]
        await self.cache.set_list_atomic(
            CATEGORIES_CACHE_KEY, items_str, ttl_seconds=self._cache_ttl_seconds
        )
        return categories

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        async with self.uow as uow:
            if not await uow.categories.exists_category_with_id(category_id):
                raise NotFoundError("Category")

            success = await uow.categories.update(category_id, data.model_dump(exclude_unset=True))
            if not success:
                raise OperationFailedError("Failed to update category")
            await uow.commit()

        await self._invalidate_cache()
        await self.pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "categories", "key": CATEGORIES_CACHE_KEY},
        )
        await self.pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "categories", "action": "update", "entity_id": category_id},
        )
        return CategoryResponse(id=category_id, message="Category updated successfully")

    async def delete_category(self, category_id: int) -> CategoryResponse:
        async with self.uow as uow:
            if not await uow.categories.exists_category_with_id(category_id):
                raise NotFoundError("Category")

            success = await uow.categories.delete(category_id)
            if not success:
                raise OperationFailedError("Failed to delete category")
            await uow.commit()

        await self._invalidate_cache()
        await self.pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "categories", "key": CATEGORIES_CACHE_KEY},
        )
        await self.pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "categories", "action": "delete", "entity_id": category_id},
        )
        return CategoryResponse(id=category_id, message="Category deleted successfully")

    async def category_id_exists(self, category_id: int) -> bool:
        async with self.uow as uow:
            return await uow.categories.exists_category_with_id(category_id)

    async def _invalidate_cache(self) -> None:
        await self.cache.delete(CATEGORIES_CACHE_KEY)
