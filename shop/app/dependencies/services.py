from fastapi import Depends

from shop.app.core.config import settings
from shop.app.dependencies.cache import get_cache_service
from shop.app.dependencies.repositories import (
    get_cart_item_repository,
    get_cart_repository,
    get_category_repository,
    get_event_log_repository,
    get_order_item_repository,
    get_order_repository,
    get_product_image_repository,
    get_product_repository,
    get_product_specification_repository,
    get_refresh_token_repository,
    get_review_repository,
    get_role_repository,
    get_user_repository,
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
from shop.app.services.analytics_service import AnalyticsService
from shop.app.services.auth_service import AuthService
from shop.app.services.cache_service import CacheService
from shop.app.services.cart_service import CartService
from shop.app.services.category_service import CategoryService
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
    category_repo: CategoryRepository = Depends(get_category_repository),
    cache: CacheService = Depends(get_cache_service),
) -> CategoryService:
    return CategoryService(
        category_repo=category_repo,
        cache=cache,
        cache_ttl_seconds=settings.CATEGORIES_CACHE_TTL_SECONDS or None,
    )


async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_service: CategoryService = Depends(get_category_service),
    cache: CacheService = Depends(get_cache_service),
) -> ProductService:
    return ProductService(
        product_repo=product_repo,
        category_service=category_service,
        cache=cache,
        cache_ttl_seconds=settings.PRODUCTS_CACHE_TTL_SECONDS or None,
    )


async def get_product_image_service(
    image_repo: ProductImageRepository = Depends(get_product_image_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductImageService:
    return ProductImageService(
        image_repo=image_repo,
        product_repo=product_repo,
    )


async def get_product_specification_service(
    specification_repo: ProductSpecificationRepository = Depends(
        get_product_specification_repository
    ),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductSpecificationService:
    return ProductSpecificationService(
        specification_repo=specification_repo,
        product_repo=product_repo,
    )


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
    cache: CacheService = Depends(get_cache_service),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        refresh_repo=refresh_repo,
        role_repo=role_repo,
        cache=cache,
    )


async def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    cart_item_repo: CartItemRepository = Depends(get_cart_item_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> CartService:
    return CartService(
        cart_repo=cart_repo,
        cart_item_repo=cart_item_repo,
        product_repo=product_repo,
    )


async def get_role_service(
    role_repo: RoleRepository = Depends(get_role_repository),
    cache: CacheService = Depends(get_cache_service),
) -> RoleService:
    return RoleService(
        role_repo=role_repo,
        cache=cache,
        cache_ttl_seconds=settings.ROLES_CACHE_TTL_SECONDS or None,
    )


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    cache: CacheService = Depends(get_cache_service),
) -> UserService:
    return UserService(
        user_repo=user_repo,
        cache=cache,
        cache_ttl_seconds=settings.USERS_CACHE_TTL_SECONDS or None,
    )


async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
) -> OrderService:
    return OrderService(
        order_repo=order_repo,
        order_item_repo=order_item_repo,
    )


async def get_order_item_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> OrderItemService:
    return OrderItemService(
        order_repo=order_repo,
        order_item_repo=order_item_repo,
        product_repo=product_repo,
    )


async def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ReviewService:
    return ReviewService(review_repo=review_repo, product_repo=product_repo)


async def get_event_log_service(
    event_repo: EventLogRepository = Depends(get_event_log_repository),
) -> EventLogService:
    return EventLogService(repo=event_repo)


async def get_analytics_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    cache: CacheService = Depends(get_cache_service),
) -> AnalyticsService:
    return AnalyticsService(
        order_repo=order_repo,
        user_repo=user_repo,
        product_repo=product_repo,
        cache=cache,
        cache_ttl_seconds=settings.ANALYTICS_CACHE_TTL_SECONDS,
    )


