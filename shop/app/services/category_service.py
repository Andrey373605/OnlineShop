from shop.app.models.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryResponse,
    CategoryUpdate,
)
from shop.app.repositories.protocols import UnitOfWork
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
        self._uow = uow
        self._cache = cache
        self._pubsub = pubsub
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_category(self, data: CategoryCreate) -> dict:
        async with self._uow as uow:
            category_id = await uow.categories.create(data.model_dump())
            await uow.commit()

        await self._after_mutation(category_id, "create")
        return {"id": category_id, "message": "Category created successfully"}

    async def get_category_by_id(self, category_id: int) -> CategoryOut:
        async with self._uow as uow:
            category = await uow.categories.get_by_id(category_id)
            return category

    async def get_all_categories(self) -> list[CategoryOut]:
        if await self._cache.exists(CATEGORIES_CACHE_KEY):
            items_str = await self._cache.get_list(CATEGORIES_CACHE_KEY)
            return [CategoryOut.model_validate_json(s) for s in items_str]

        async with self._uow as uow:
            categories = await uow.categories.get_all()

        items_str = [c.model_dump_json() for c in categories]
        await self._cache.set_list_atomic(
            CATEGORIES_CACHE_KEY, items_str, ttl_seconds=self._cache_ttl_seconds
        )
        return categories

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        async with self._uow as uow:

            category = await uow.categories.update(category_id, data.model_dump(exclude_unset=True))

            await uow.commit()

        await self._after_mutation(category_id, "update")
        return CategoryResponse(id=category_id, message="Category updated successfully")

    async def delete_category(self, category_id: int) -> CategoryResponse:
        async with self._uow as uow:

            await uow.categories.delete(category_id)
            await uow.commit()

        await self._after_mutation(category_id, "delete")
        return CategoryResponse(id=category_id, message="Category deleted successfully")

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
