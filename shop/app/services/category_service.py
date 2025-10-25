from fastapi import HTTPException

from shop.app.db import queries
from shop.app.shemas.category_shemas import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    async def create_category(conn, data: CategoryCreate):
        result = await queries.create_category(conn, **data.model_dump())
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create product")
        return {"id": result['id'], "message": "Category created successfully"}

    @staticmethod
    async def get_category_by_id(conn, category_id: int):
        result = await queries.get_category_by_id(conn, id=category_id)
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return dict(result)

    @staticmethod
    async def get_all_categories(conn):
        result = await queries.get_all_categories(conn)
        return [dict(r) for r in result]

    @staticmethod
    async def update_category(conn, category_id: int, data: CategoryUpdate):
        result = await queries.update_category(conn, id=category_id, **data.model_dump())
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"id": result["id"], "message": "Category updated successfully"}

    @staticmethod
    async def delete_category(conn, category_id: int):
        result = await queries.delete_category(conn, id=category_id)
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"id": result["id"], "message": "Category deleted successfully"}

