"""PostgreSQL repository implementations."""

from shop.app.infrastructure.persistence.postgres.repositories.brand_repository import (
    BrandRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.cart_item_repository import (
    CartItemRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.cart_repository import (
    CartRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.category_repository import (
    CategoryRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.order_item_repository import (
    OrderItemRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.order_repository import (
    OrderRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.permission_repository import (
    PermissionRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.product_details_repository import (
    ProductDetailsRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.product_image_repository import (
    ProductImageRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.product_repository import (
    ProductRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.product_variant_details_repository import (
    ProductVariantDetailsRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.product_variant_repository import (
    ProductVariantRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.review_repository import (
    ReviewRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.role_repository import (
    RoleRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.stock_movement_repository import (
    StockMovementRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.user_repository import (
    UserRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.warehouse_repository import (
    WarehouseRepositorySql,
)

__all__ = [
    "BrandRepositorySql",
    "CartItemRepositorySql",
    "CartRepositorySql",
    "CategoryRepositorySql",
    "OrderItemRepositorySql",
    "OrderRepositorySql",
    "PermissionRepositorySql",
    "ProductDetailsRepositorySql",
    "ProductImageRepositorySql",
    "ProductRepositorySql",
    "ProductVariantDetailsRepositorySql",
    "ProductVariantRepositorySql",
    "ReviewRepositorySql",
    "RoleRepositorySql",
    "StockMovementRepositorySql",
    "UserRepositorySql",
    "WarehouseRepositorySql",
]
