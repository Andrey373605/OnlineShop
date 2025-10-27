from fastapi import APIRouter, Depends, Body, Path
from shop.app.dependencies.services import get_category_service
from shop.app.services.category_service import CategoryService
from shop.app.schemas.category_schemas import CategoryResponse, CategoryCreate, CategoryUpdate

router = APIRouter(prefix='/categories', tags=['Categories'])


@router.post("/", response_model=CategoryResponse)
async def create_category(data: CategoryCreate = Body(),
                          category_service: CategoryService = Depends(get_category_service)):
    return await category_service.create_category(data)


@router.get("/{category_id}")
async def get_category_by_id(category_id: int = Path(),
                             category_service: CategoryService = Depends(get_category_service)):
    return await category_service.get_category_by_id(category_id)


@router.get("/")
async def get_all_categories(category_service: CategoryService = Depends(get_category_service)):
    return await category_service.get_all_categories()


@router.put("/{category_id}")
async def update_category(category_id: int = Path(),
                          data: CategoryUpdate = Body(),
                          category_service: CategoryService = Depends(get_category_service)):
    return await category_service.update_category(category_id, data)


@router.delete("/{category_id}")
async def delete_category(category_id: int = Path(),
                          category_service: CategoryService = Depends(get_category_service)):
        return await category_service.delete_category(category_id)
