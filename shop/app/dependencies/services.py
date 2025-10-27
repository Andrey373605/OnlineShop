from fastapi import Depends
from shop.app.core.db import get_db, queries
from shop.app.repositories.category_repository import CategoryRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.services.category_service import CategoryService
from shop.app.services.product_service import ProductService


async def get_category_repository(conn = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(conn=conn, queries=queries)

async def get_product_repository(conn = Depends(get_db)) -> ProductRepository:
    return ProductRepository(conn=conn, queries=queries)

async def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    return CategoryService(category_repo)

async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_service: CategoryService = Depends(get_category_service)
) -> ProductService:
    return ProductService(product_repo, category_service)