import asyncpg
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from shop.app.core.db import queries
from shop.app.dependencies.db import get_db
from shop.app.dependencies.mongo import get_mongo_db
from shop.app.repositories.cart_item_repository import CartItemRepositorySql
from shop.app.repositories.cart_repository import CartRepositorySql
from shop.app.repositories.category_repository import CategoryRepositorySql
from shop.app.repositories.event_log_mongo_repository import EventLogRepositoryMongo
from shop.app.repositories.event_log_repository import EventLogRepositorySql
from shop.app.repositories.order_item_repository import OrderItemRepositorySql
from shop.app.repositories.order_repository import OrderRepositorySql
from shop.app.repositories.product_image_repository import ProductImageRepositorySql
from shop.app.repositories.product_repository import ProductRepositorySql
from shop.app.repositories.product_specification_repository import (
    ProductSpecificationRepositorySql,
)
from shop.app.repositories.protocols import (
    CartItemRepository,
    CartRepository,
    CategoryRepository,
    EventLogRepository,
    OrderItemRepository,
    OrderRepository,
    ProductImageRepository,
    ProductRepository,
    ProductSpecificationRepository,
    RefreshTokenRepository,
    ReviewRepository,
    RoleRepository,
    UserRepository,
)
from shop.app.repositories.refresh_token_repository import RefreshTokenRepositorySql
from shop.app.repositories.review_repository import ReviewRepositorySql
from shop.app.repositories.role_repository import RoleRepositorySql
from shop.app.repositories.user_repository import UserRepositorySql


async def get_category_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> CategoryRepository:
    return CategoryRepositorySql(conn=conn, queries=queries)


async def get_product_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> ProductRepository:
    return ProductRepositorySql(conn=conn, queries=queries)


async def get_user_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> UserRepository:
    return UserRepositorySql(conn=conn, queries=queries)


async def get_role_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> RoleRepository:
    return RoleRepositorySql(conn=conn, queries=queries)


async def get_product_specification_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> ProductSpecificationRepository:
    return ProductSpecificationRepositorySql(conn=conn, queries=queries)


async def get_product_image_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> ProductImageRepository:
    return ProductImageRepositorySql(conn=conn, queries=queries)


async def get_cart_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> CartRepository:
    return CartRepositorySql(conn=conn, queries=queries)


async def get_cart_item_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> CartItemRepository:
    return CartItemRepositorySql(conn=conn, queries=queries)


async def get_review_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> ReviewRepository:
    return ReviewRepositorySql(conn=conn, queries=queries)


async def get_order_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> OrderRepository:
    return OrderRepositorySql(conn=conn, queries=queries)


async def get_order_item_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> OrderItemRepository:
    return OrderItemRepositorySql(conn=conn, queries=queries)


async def get_event_log_repository(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
) -> EventLogRepository:
    return EventLogRepositoryMongo(db=db)


async def get_refresh_token_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> RefreshTokenRepository:
    return RefreshTokenRepositorySql(conn=conn, queries=queries)
