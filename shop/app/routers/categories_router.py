from fastapi import APIRouter, Depends, Body, Path
from shop.app.db import get_db
from shop.app.services.category_service import CategoryService
from shop.app.shemas.category_shemas import CategoryResponse, CategoryCreate, CategoryUpdate

router = APIRouter(prefix='/categories', tags=['Categories'])

@router.post("/", response_model=CategoryResponse)
async def create_category(data: CategoryCreate = Body(),
                          conn = Depends(get_db)):
        return await CategoryService.create_category(conn, data)

@router.get("/{category_id}")
async def get_category_by_id(category_id: int = Path(),
                             conn = Depends(get_db)):
        return await CategoryService.get_category_by_id(conn, category_id)

@router.get("/")
async def get_category_by_id(conn = Depends(get_db)):
        return await CategoryService.get_all_categories(conn)

@router.put("/{category_id}")
async def update_category(category_id: int = Path(),
                          data: CategoryUpdate = Body(),
                          conn = Depends(get_db)):
        return await CategoryService.update_category(conn, category_id, data)

@router.delete("/{category_id}")
async def update_category(category_id: int = Path(),
                          db=Depends(get_db)):
    async with db.acquire() as conn:
        return await CategoryService.delete_category(conn, category_id)