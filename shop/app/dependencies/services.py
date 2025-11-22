from fastapi import Depends
from shop.app.dependencies.repositories import (
    get_cart_item_repository,
    get_cart_repository,
    get_category_repository,
    get_order_item_repository,
    get_order_repository,
    get_product_image_repository,
    get_product_repository,
    get_product_specification_repository,
    get_refresh_token_repository,
    get_review_repository,
    get_role_repository,
    get_user_repository, get_event_log_repository,
)
from shop.app.repositories.cart_item_repository import CartItemRepository
from shop.app.repositories.cart_repository import CartRepository
from shop.app.repositories.category_repository import CategoryRepository
from shop.app.repositories.event_log_repository import EventLogRepository
from shop.app.repositories.product_image_repository import ProductImageRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.repositories.product_specification_repository import (
    ProductSpecificationRepository,
)
from shop.app.repositories.refresh_token_repository import RefreshTokenRepository
from shop.app.repositories.review_repository import ReviewRepository
from shop.app.repositories.role_repository import RoleRepository
from shop.app.repositories.user_repository import UserRepository
from shop.app.repositories.order_repository import OrderRepository
from shop.app.repositories.order_item_repository import OrderItemRepository
from shop.app.services.cart_service import CartService
from shop.app.services.category_service import CategoryService
from shop.app.services.product_image_service import ProductImageService
from shop.app.services.product_service import ProductService
from shop.app.services.product_specification_service import (
    ProductSpecificationService,
)
from shop.app.services.auth_service import AuthService
from shop.app.services.event_log_service import EventLogService
from shop.app.services.review_service import ReviewService
from shop.app.services.role_service import RoleService
from shop.app.services.user_service import UserService
from shop.app.services.order_service import OrderService
from shop.app.services.order_item_service import OrderItemService


async def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    return CategoryService(category_repo)

async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_service: CategoryService = Depends(get_category_service)
) -> ProductService:
    return ProductService(product_repo, category_service)


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
) -> AuthService:
    return AuthService(user_repo=user_repo, refresh_repo=refresh_repo)


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
) -> RoleService:
    return RoleService(role_repo)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
) -> OrderService:
    return OrderService(order_repo, order_item_repo)


async def get_order_item_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> OrderItemService:
    return OrderItemService(order_repo, order_item_repo, product_repo)


async def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ReviewService:
    return ReviewService(review_repo=review_repo, product_repo=product_repo)


async def get_event_log_service(
    event_repo: EventLogRepository = Depends(get_event_log_repository),
) -> EventLogService:
    return EventLogService(repo=event_repo)
