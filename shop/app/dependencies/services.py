from fastapi import Depends
from shop.app.dependencies.repositories import (
    get_category_repository,
    get_product_repository,
    get_refresh_token_repository,
    get_user_repository,
)
from shop.app.repositories.category_repository import CategoryRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.repositories.refresh_token_repository import RefreshTokenRepository
from shop.app.repositories.user_repository import UserRepository
from shop.app.services.category_service import CategoryService
from shop.app.services.product_service import ProductService
from shop.app.services.auth_service import AuthService


async def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    return CategoryService(category_repo)

async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_service: CategoryService = Depends(get_category_service)
) -> ProductService:
    return ProductService(product_repo, category_service)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthService:
    return AuthService(user_repo=user_repo, refresh_repo=refresh_repo)
