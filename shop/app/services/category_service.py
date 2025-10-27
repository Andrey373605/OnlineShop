from fastapi import HTTPException
from shop.app.repositories.category_repository import CategoryRepository
from shop.app.schemas.category_schemas import CategoryCreate, CategoryUpdate, CategoryOut, CategoryResponse


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def create_category(self, data: CategoryCreate) -> dict:
        check_exist = await self._category_name_exists(data.name)
        if check_exist:
            raise HTTPException(status_code=400, detail="Category name already exists")

        category_id = await self.category_repo.create(data.model_dump())

        if not category_id:
            raise HTTPException(status_code=500, detail="Failed to create category")

        return {"id": category_id, "message": "Category created successfully"}

    async def get_category_by_id(self, category_id: int) -> CategoryOut:
        category = await self.category_repo.get_by_id(category_id)

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return category

    async def get_all_categories(self) -> list[CategoryOut]:
        categories = await self.category_repo.get_all()
        return categories

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryResponse:
        check_exist = await self._category_id_exists(category_id)
        if not check_exist:
            raise HTTPException(status_code=404, detail="Category not found")

        success = await self.category_repo.update(category_id, data.model_dump(exclude_unset=True))

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update category")

        return CategoryResponse(id=category_id, message="Category updated successfully")

    async def delete_category(self, category_id: int) -> CategoryResponse:
        check_exist = await self._category_id_exists(category_id)
        if not check_exist:
            raise HTTPException(status_code=404, detail="Category not found")

        # Бизнес-логика: можно ли удалять?
        # if category.has_products():
        #     raise HTTPException(status_code=400, detail="Cannot delete category with products")

        success = await self.category_repo.delete(category_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete category")

        return CategoryResponse(id=category_id, message="Category deleted successfully")

    async def category_id_exists(self, category_id: int) -> bool:
        return await self.category_repo.exists_category_with_id(category_id)

    async def _category_name_exists(self, name: str) -> bool:
        return await self.category_repo.exists_category_with_name(name)
