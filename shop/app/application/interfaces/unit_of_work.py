from abc import ABC, abstractmethod

from shop.app.application.interfaces.repositories.brand_repository import BrandRepository
from shop.app.application.interfaces.repositories.cart_repository import CartRepository
from shop.app.application.interfaces.repositories.category_repository import CategoryRepository
from shop.app.application.interfaces.repositories.order_repository import OrderRepository
from shop.app.application.interfaces.repositories.permission_repository import PermissionRepository
from shop.app.application.interfaces.repositories.product_details_repository import (
    ProductDetailsRepository,
)
from shop.app.application.interfaces.repositories.product_image_repository import (
    ProductImageRepository,
)
from shop.app.application.interfaces.repositories.product_repository import ProductRepository
from shop.app.application.interfaces.repositories.product_variant_details_repository import (
    ProductVariantDetailsRepository,
)
from shop.app.application.interfaces.repositories.product_variant_repository import (
    ProductVariantRepository,
)
from shop.app.application.interfaces.repositories.review_repository import ReviewRepository
from shop.app.application.interfaces.repositories.role_repository import RoleRepository
from shop.app.application.interfaces.repositories.stock_movement_repository import (
    StockMovementRepository,
)
from shop.app.application.interfaces.repositories.user_repository import UserRepository
from shop.app.application.interfaces.repositories.warehouse_repository import (
    WarehouseRepository,
)


class UnitOfWork(ABC):
    """Transaction boundary for domain persistence only."""

    categories: CategoryRepository
    brands: BrandRepository
    products: ProductRepository
    product_variants: ProductVariantRepository
    product_details: ProductDetailsRepository
    product_variant_details: ProductVariantDetailsRepository
    product_images: ProductImageRepository
    users: UserRepository
    permissions: PermissionRepository
    roles: RoleRepository
    carts: CartRepository
    orders: OrderRepository
    reviews: ReviewRepository
    warehouses: WarehouseRepository
    stock_movements: StockMovementRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Begin a transactional scope and wire repositories."""

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Rollback on failure or release resources."""

    @abstractmethod
    async def commit(self) -> None:
        """Persist all changes in the current transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Discard all changes in the current transaction."""
