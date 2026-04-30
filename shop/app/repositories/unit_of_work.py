import asyncpg
from asyncpg.connection import Connection
from asyncpg.transaction import Transaction

from shop.app.repositories.cart_item_repository import CartItemRepositorySql
from shop.app.repositories.cart_repository import CartRepositorySql
from shop.app.repositories.category_repository import CategoryRepositorySql
from shop.app.repositories.order_item_repository import OrderItemRepositorySql
from shop.app.repositories.order_repository import OrderRepositorySql
from shop.app.repositories.product_image_repository import ProductImageRepositorySql
from shop.app.repositories.product_repository import ProductRepositorySql
from shop.app.repositories.product_specification_repository import (
    ProductSpecificationRepositorySql,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.repositories.refresh_token_repository import RefreshTokenRepositorySql
from shop.app.repositories.review_repository import ReviewRepositorySql
from shop.app.repositories.role_repository import RoleRepositorySql
from shop.app.repositories.user_repository import UserRepositorySql


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
        self.categories = CategoryRepositorySql(self._conn)
        self.products = ProductRepositorySql(self._conn)
        self.users = UserRepositorySql(self._conn)
        self.roles = RoleRepositorySql(self._conn)
        self.product_specifications = ProductSpecificationRepositorySql(self._conn)
        self.product_images = ProductImageRepositorySql(self._conn)
        self.carts = CartRepositorySql(self._conn)
        self.cart_items = CartItemRepositorySql(self._conn)
        self.reviews = ReviewRepositorySql(self._conn)
        self.orders = OrderRepositorySql(self._conn)
        self.order_items = OrderItemRepositorySql(self._conn)
        self.refresh_tokens = RefreshTokenRepositorySql(self._conn)