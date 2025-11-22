from fastapi import Depends

from shop.app.core.db import get_db, queries
from shop.app.repositories.category_repository import CategoryRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.repositories.user_repository import UserRepository
from shop.app.repositories.role_repository import RoleRepository
from shop.app.repositories.product_specification_repository import (
    ProductSpecificationRepository,
)
from shop.app.repositories.product_image_repository import ProductImageRepository
from shop.app.repositories.cart_repository import CartRepository
from shop.app.repositories.cart_item_repository import CartItemRepository
from shop.app.repositories.review_repository import ReviewRepository
from shop.app.repositories.order_repository import OrderRepository
from shop.app.repositories.order_item_repository import OrderItemRepository
from shop.app.repositories.event_log_repository import EventLogRepository
from shop.app.repositories.refresh_token_repository import RefreshTokenRepository


async def get_category_repository(conn = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(conn=conn, queries=queries)

async def get_product_repository(conn = Depends(get_db)) -> ProductRepository:
    return ProductRepository(conn=conn, queries=queries)


async def get_user_repository(conn = Depends(get_db)) -> UserRepository:
    return UserRepository(conn=conn, queries=queries)


async def get_role_repository(conn = Depends(get_db)) -> RoleRepository:
    return RoleRepository(conn=conn, queries=queries)


async def get_product_specification_repository(
    conn = Depends(get_db),
) -> ProductSpecificationRepository:
    return ProductSpecificationRepository(conn=conn, queries=queries)


async def get_product_image_repository(
    conn = Depends(get_db),
) -> ProductImageRepository:
    return ProductImageRepository(conn=conn, queries=queries)


async def get_cart_repository(conn = Depends(get_db)) -> CartRepository:
    return CartRepository(conn=conn, queries=queries)


async def get_cart_item_repository(conn = Depends(get_db)) -> CartItemRepository:
    return CartItemRepository(conn=conn, queries=queries)


async def get_review_repository(conn = Depends(get_db)) -> ReviewRepository:
    return ReviewRepository(conn=conn, queries=queries)


async def get_order_repository(conn = Depends(get_db)) -> OrderRepository:
    return OrderRepository(conn=conn, queries=queries)


async def get_order_item_repository(conn = Depends(get_db)) -> OrderItemRepository:
    return OrderItemRepository(conn=conn, queries=queries)


async def get_event_log_repository(conn = Depends(get_db)) -> EventLogRepository:
    return EventLogRepository(conn=conn, queries=queries)


async def get_refresh_token_repository(
    conn = Depends(get_db),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(conn=conn, queries=queries)

