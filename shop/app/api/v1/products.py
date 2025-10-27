from fastapi import APIRouter, Depends, Body, Path
from shop.app.core.db import get_db
from shop.app.dependencies.pagination import CommonPaginationParams
from shop.app.dependencies.services import get_product_service
from shop.app.services.product_service import ProductService
from shop.app.schemas.product_schemas import ProductResponse, ProductCreate, ProductUpdate

router = APIRouter(prefix='/products', tags=['Products'])


@router.post("/", response_model=ProductResponse)
async def create_product(data: ProductCreate = Body(),
                         product_service: ProductService = Depends(get_product_service)):
    return await product_service.create_product(data)


@router.get("/{product_id}")
async def get_product_by_id(product_id: int = Path(),
                            product_service: ProductService = Depends(get_product_service)):
    return await product_service.get_product_by_id(product_id)


@router.get("/")
async def get_all_products(product_service: ProductService = Depends(get_product_service),
                           pagination: CommonPaginationParams = Depends(CommonPaginationParams)):
    return await product_service.get_all_products(limit=pagination.limit, offset=pagination.offset)


@router.put("/{product_id}")
async def update_product(product_id: int = Path(),
                         data: ProductUpdate = Body(),
                         product_service: ProductService = Depends(get_product_service)):
    return await product_service.update_product(product_id, data)


@router.delete("/{product_id}")
async def delete_product(product_id: int = Path(),
                         product_service: ProductService = Depends(get_product_service)):
        return await product_service.delete_product(product_id)
