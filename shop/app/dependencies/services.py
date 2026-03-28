from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from shop.app.core.config import settings
from shop.app.dependencies.cache import get_cache_service
from shop.app.dependencies.db import get_uow
from shop.app.dependencies.mongo import get_mongo_db
from shop.app.repositories.event_log_analytics_repository import EventLogAnalyticsRepositoryMongo
from shop.app.repositories.event_log_mongo_repository import EventLogRepositoryMongo
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.auth_service import AuthService
from shop.app.services.cache_service import CacheService
from shop.app.services.cart_service import CartService
from shop.app.services.category_service import CategoryService
from shop.app.services.event_log_analytics_service import EventLogAnalyticsService
from shop.app.services.event_log_service import EventLogService
from shop.app.services.order_item_service import OrderItemService
from shop.app.services.order_service import OrderService
from shop.app.services.product_image_service import ProductImageService
from shop.app.services.product_service import ProductService
from shop.app.services.product_specification_service import (
    ProductSpecificationService,
)
from shop.app.services.review_service import ReviewService
from shop.app.services.role_service import RoleService
from shop.app.services.user_service import UserService


async def get_category_service(
    uow: UnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> CategoryService:
    return CategoryService(
        uow=uow,
        cache=cache,
        cache_ttl_seconds=settings.CATEGORIES_CACHE_TTL_SECONDS or None,
    )


async def get_product_service(
    uow: UnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> ProductService:
    return ProductService(
        uow=uow,
        cache=cache,
        cache_ttl_seconds=settings.PRODUCTS_CACHE_TTL_SECONDS or None,
    )


async def get_product_image_service(
    uow: UnitOfWork = Depends(get_uow),
) -> ProductImageService:
    return ProductImageService(uow=uow)


async def get_product_specification_service(
    uow: UnitOfWork = Depends(get_uow),
) -> ProductSpecificationService:
    return ProductSpecificationService(uow=uow)


async def get_auth_service(
    uow: UnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> AuthService:
    return AuthService(uow=uow, cache=cache)


async def get_cart_service(
    uow: UnitOfWork = Depends(get_uow),
) -> CartService:
    return CartService(uow=uow)


async def get_role_service(
    uow: UnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> RoleService:
    return RoleService(
        uow=uow,
        cache=cache,
        cache_ttl_seconds=settings.ROLES_CACHE_TTL_SECONDS or None,
    )


async def get_user_service(
    uow: UnitOfWork = Depends(get_uow),
    cache: CacheService = Depends(get_cache_service),
) -> UserService:
    return UserService(
        uow=uow,
        cache=cache,
        cache_ttl_seconds=settings.USERS_CACHE_TTL_SECONDS or None,
    )


async def get_order_service(
    uow: UnitOfWork = Depends(get_uow),
) -> OrderService:
    return OrderService(uow=uow)


async def get_order_item_service(
    uow: UnitOfWork = Depends(get_uow),
) -> OrderItemService:
    return OrderItemService(uow=uow)


async def get_review_service(
    uow: UnitOfWork = Depends(get_uow),
) -> ReviewService:
    return ReviewService(uow=uow)


async def get_event_log_service(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
) -> EventLogService:
    return EventLogService(repo=EventLogRepositoryMongo(db=db))


async def get_event_log_analytics_service(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
) -> EventLogAnalyticsService:
    return EventLogAnalyticsService(repo=EventLogAnalyticsRepositoryMongo(db=db))