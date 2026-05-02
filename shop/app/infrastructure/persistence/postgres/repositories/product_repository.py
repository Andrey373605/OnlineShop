from decimal import Decimal
from typing import Any, Mapping
from uuid import UUID

import asyncpg

from shop.app.domain.entities.product import Product
from shop.app.infrastructure.persistence.postgres.repositories.exceptions import (
    RepositoryForeignKeyError,
    RepositoryMappingError,
    RepositoryUnexpectedResultError,
    RepositoryUniqueConstraintError,
    RepositoryUnavailableError,
)
from shop.app.application.interfaces.repositories import ProductRepository


class ProductRepositorySql(ProductRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, product_id: UUID) -> Product | None:
        try:
            row = await self._conn.fetchrow(
                """
                SELECT id, title, description, price, stock, brand, thumbnail_key, is_published, category_id
                FROM products
                WHERE id = $1;
                """,
                product_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch product") from exc

        return self._map_row(row) if row else None

    async def list_published(self, limit: int, offset: int) -> list[Product]:
        try:
            rows = await self._conn.fetch(
                """
                SELECT id, title, description, price, stock, brand, thumbnail_key, is_published, category_id
                FROM products
                WHERE is_published = TRUE
                ORDER BY id
                LIMIT $1 OFFSET $2;
                """,
                limit,
                offset,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch products") from exc

        return [self._map_row(row) for row in rows]

    async def get_total(self) -> int:
        try:
            row = await self._conn.fetchrow("SELECT COUNT(*) AS total FROM products;")
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to count products") from exc

        return row["total"]

    async def list_by_category(self, category_id: UUID) -> list[Product]:
        try:
            rows = await self._conn.fetch(
                """
                SELECT id, title, description, price, stock, brand, thumbnail_key, is_published, category_id
                FROM products
                WHERE category_id = $1
                ORDER BY id;
                """,
                category_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch products by category") from exc

        return [self._map_row(row) for row in rows]

    async def add(self, product: Product) -> None:
        try:
            await self._conn.execute(
                """
                INSERT INTO products (
                    title, description, price, stock, brand, thumbnail_key, is_published, category_id
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                product.title,
                product.description,
                product.price,
                product.stock,
                product.brand,
                product.thumbnail_key,
                product.is_published,
                product.category_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Category does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Product violates a unique constraint") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to create product") from exc

    async def update(self, product: Product) -> None:
        try:
            await self._conn.execute(
                """
                UPDATE products
                SET title = $2,
                    description = $3,
                    price = $4,
                    stock = $5,
                    brand = $6,
                    thumbnail_key = $7,
                    is_published = $8,
                    category_id = $9,
                    updated_at = NOW()
                WHERE id = $1
                """,
                product.id,
                product.title,
                product.description,
                product.price,
                product.stock,
                product.brand,
                product.thumbnail_key,
                product.is_published,
                product.category_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Category does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Product violates a unique constraint") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to update product") from exc

    async def delete(self, product_id: UUID) -> None:
        try:
            await self._conn.execute(
                "DELETE FROM products WHERE id = $1;",
                product_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Product is referenced by another entity") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete product") from exc

    # Backward-compatible aliases.
    async def get_all(self, limit: int, offset: int) -> list[Product]:
        return await self.list_published(limit, offset)

    async def create(self, product_data) -> Product:
        created = await self._conn.fetchrow(
            """
            INSERT INTO products (
                title, description, price, stock, brand, thumbnail_key, is_published, category_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, title, description, price, stock, brand, thumbnail_key, is_published, category_id;
            """,
            product_data.title,
            product_data.description,
            product_data.price,
            product_data.stock,
            product_data.brand,
            product_data.thumbnail_key,
            product_data.is_published,
            product_data.category_id,
        )
        if not created:
            raise RepositoryUnexpectedResultError("Database did not return created product")
        return self._map_row(created)

    async def exists_product_with_id(self, product_id: UUID) -> bool:
        try:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM products WHERE id = $1) AS exists;",
                product_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to check product") from exc

        return row["exists"]

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> Product:
        try:
            raw_price = row["price"]
            price = raw_price if isinstance(raw_price, Decimal) else Decimal(str(raw_price))

            raw_thumb = row["thumbnail_key"]
            thumbnail_key = "" if raw_thumb is None else str(raw_thumb)

            return Product(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                price=price,
                stock=row["stock"],
                brand=row["brand"],
                is_published=row["is_published"],
                category_id=row["category_id"],
                thumbnail_key=thumbnail_key,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RepositoryMappingError("Product row has invalid shape") from exc
