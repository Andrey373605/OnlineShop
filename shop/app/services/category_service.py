from fastapi import HTTPException

from shop.app.repositories.category_repository import CategoryRepository
from shop.app.schemas.category_schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryResponse,
    CategoryUpdate,
)
from shop.app.services.cache_service import CacheService

CATEGORIES_CACHE_KEY = "categories:all"


class CategoryService:
    def __init__(
        self,
        category_repo: CategoryRepository,
        cache: CacheService,
        cache_ttl_seconds: int | None = None,
    ):
        self.category_repo = category_repo
        self.cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_category(self, data: CategoryCreate) -> dict:
        check_exist = await self._category_name_exists(data.name)
        if check_exist:
            raise HTTPException(status_code=400, detail="Category name already exists")

        category_id = await self.category_repo.create(data.model_dump())

        if not category_id:
            raise HTTPException(status_code=500, detail="Failed to create category")

        await self._invalidate_cache()
        return {"id": category_id, "message": "Category created successfully"}

    async def get_category_by_id(self, category_id: int) -> CategoryOut:
        category = await self.category_repo.get_by_id(category_id)

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return category

    async def get_all_categories(self) -> list[CategoryOut]:
        if await self.cache.exists(CATEGORIES_CACHE_KEY):
            items_str = await self.cache.get_list(CATEGORIES_CACHE_KEY)
            return [CategoryOut.model_validate_json(s) for s in items_str]
        categories = await self.category_repo.get_all()
        items_str = [c.model_dump_json() for c in categories]
        await self.cache.set_list_atomic(
            CATEGORIES_CACHE_KEY, items_str, ttl_seconds=self._cache_ttl_seconds
        )
        return categories

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        check_exist = await self.category_id_exists(category_id)
        if not check_exist:
            raise HTTPException(status_code=404, detail="Category not found")

        success = await self.category_repo.update(category_id, data.model_dump(exclude_unset=True))

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update category")

        await self._invalidate_cache()
        return CategoryResponse(id=category_id, message="Category updated successfully")

    async def delete_category(self, category_id: int) -> CategoryResponse:
        check_exist = await self.category_id_exists(category_id)
        if not check_exist:
            raise HTTPException(status_code=404, detail="Category not found")

        # Бизнес-логика: можно ли удалять?
        # if category.has_products():
        #     raise HTTPException(status_code=400, detail="Cannot delete category with products")

        success = await self.category_repo.delete(category_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete category")

        await self._invalidate_cache()
        return CategoryResponse(id=category_id, message="Category deleted successfully")

    async def _invalidate_cache(self) -> None:
        await self.cache.delete(CATEGORIES_CACHE_KEY)

    async def category_id_exists(self, category_id: int) -> bool:
        return await self.category_repo.exists_category_with_id(category_id)

    async def _category_name_exists(self, name: str) -> bool:
        return await self.category_repo.exists_category_with_name(name)
