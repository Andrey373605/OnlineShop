import asyncpg
from asyncpg.connection import Connection
from asyncpg.transaction import Transaction
from typing import cast

from shop.app.application.interfaces.repositories.cart_item_repository import (
    CartItemRepository,
)
from shop.app.application.interfaces.repositories.order_item_repository import (
    OrderItemRepository,
)
from shop.app.application.interfaces.repositories.product_specification_repository import (
    ProductSpecificationRepository,
)
from shop.app.application.interfaces.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from shop.app.application.interfaces.repositories import (
    BrandRepository,
    CartRepository,
    CategoryRepository,
    OrderRepository,
    PermissionRepository,
    ProductDetailsRepository,
    ProductImageRepository,
    ProductRepository,
    ProductVariantDetailsRepository,
    ProductVariantRepository,
    ReviewRepository,
    RoleRepository,
    StockMovementRepository,
    UnitOfWork,
    UserRepository,
    WarehouseRepository,
)
from shop.app.infrastructure.persistence.postgres.repositories.cart_item_repository import (
    CartItemRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.cart_repository import (
    CartRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.brand_repository import (
    BrandRepositorySql,
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
from shop.app.infrastructure.persistence.postgres.repositories.product_image_repository import (
    ProductImageRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.permission_repository import (
    PermissionRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.product_details_repository import (
    ProductDetailsRepositorySql,
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
from shop.app.infrastructure.persistence.postgres.repositories.product_specification_repository import (
    ProductSpecificationRepositorySql,
)
from shop.app.infrastructure.persistence.postgres.repositories.refresh_token_repository import (
    RefreshTokenRepositorySql,
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


class SqlUnitOfWork(UnitOfWork):

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool: asyncpg.Pool = pool

    async def __aenter__(self) -> "SqlUnitOfWork":
        self._conn: Connection = await self._pool.acquire()
        self._tx: Transaction = self._conn.transaction()
        await self._tx.start()
        self._committed = False
        self._init_repositories()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if not self._committed:
                await self._tx.rollback()
        finally:
            await self._pool.release(self._conn)

    async def commit(self) -> None:
        await self._tx.commit()
        self._committed = True

    async def rollback(self) -> None:
        await self._tx.rollback()

    def _init_repositories(self) -> None:
        c = self._conn
        self.categories = cast(CategoryRepository, CategoryRepositorySql(c))
        self.brands = cast(BrandRepository, BrandRepositorySql(c))
        self.products = cast(ProductRepository, ProductRepositorySql(c))
        self.product_variants = cast(ProductVariantRepository, ProductVariantRepositorySql(c))
        self.product_details = cast(ProductDetailsRepository, ProductDetailsRepositorySql(c))
        self.product_variant_details = cast(
            ProductVariantDetailsRepository, ProductVariantDetailsRepositorySql(c)
        )
        self.product_images = cast(ProductImageRepository, ProductImageRepositorySql(c))
        self.users = cast(UserRepository, UserRepositorySql(c))
        self.permissions = cast(PermissionRepository, PermissionRepositorySql(c))
        self.roles = cast(RoleRepository, RoleRepositorySql(c))
        self.carts = cast(CartRepository, CartRepositorySql(c))
        self.orders = cast(OrderRepository, OrderRepositorySql(c))
        self.reviews = cast(ReviewRepository, ReviewRepositorySql(c))
        self.warehouses = cast(WarehouseRepository, WarehouseRepositorySql(c))
        self.stock_movements = cast(StockMovementRepository, StockMovementRepositorySql(c))

        self.refresh_tokens = cast(RefreshTokenRepository, RefreshTokenRepositorySql(c))
        self.product_specifications = cast(
            ProductSpecificationRepository, ProductSpecificationRepositorySql(c)
        )
        self.cart_items = cast(CartItemRepository, CartItemRepositorySql(c))
        self.order_items = cast(OrderItemRepository, OrderItemRepositorySql(c))
