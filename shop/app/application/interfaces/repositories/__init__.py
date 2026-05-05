"""Domain repository ports (ABC)."""

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
from shop.app.application.interfaces.unit_of_work import UnitOfWork
from shop.app.application.interfaces.repositories.user_repository import UserRepository
from shop.app.application.interfaces.repositories.warehouse_repository import (
    WarehouseRepository,
)

__all__ = [
    "BrandRepository",
    "CartRepository",
    "CategoryRepository",
    "OrderRepository",
    "PermissionRepository",
    "ProductDetailsRepository",
    "ProductImageRepository",
    "ProductRepository",
    "ProductVariantDetailsRepository",
    "ProductVariantRepository",
    "ReviewRepository",
    "RoleRepository",
    "StockMovementRepository",
    "UnitOfWork",
    "UserRepository",
    "WarehouseRepository",
]
