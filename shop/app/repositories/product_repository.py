from decimal import Decimal
from typing import Any, Mapping

import asyncpg

from shop.app.models.domain.product import (
    ProductCreateData,
    Product,
    ProductUpdateData,
)
from shop.app.repositories.exceptions import (
    RepositoryForeignKeyError,
    RepositoryMappingError,
    RepositoryRecordNotFoundError,
    RepositoryUnexpectedResultError,
    RepositoryUniqueConstraintError,
    RepositoryUnavailableError,
)
from shop.app.repositories.protocols import ProductRepository


class ProductRepositorySql(ProductRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, product_id: int) -> Product:
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

        if not row:
            raise RepositoryRecordNotFoundError(
                "Product not found",
            )

        return self._map_row(row)

    async def get_all(self, limit: int, offset: int) -> list[Product]:
        try:
            rows = await self._conn.fetch(
                """
                SELECT id, title, description, price, stock, brand, thumbnail_key, is_published, category_id
                FROM products
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

    async def create(self, product_data: ProductCreateData) -> Product:
        try:
            row = await self._conn.fetchrow(
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
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Category does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Product violates a unique constraint") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to create product") from exc

        if not row:
            raise RepositoryUnexpectedResultError("Database did not return created product")

        return self._map_row(row)

    async def update(self, product_id: int, update_data: ProductUpdateData) -> Product:
        normalized_data = self._normalize_update_data(update_data)

        try:
            row = await self._conn.fetchrow(
                """
                UPDATE products
                SET title = COALESCE($2, title),
                    description = COALESCE($3, description),
                    price = COALESCE($4, price),
                    stock = COALESCE($5, stock),
                    brand = COALESCE($6, brand),
                    thumbnail_key = COALESCE($7, thumbnail_key),
                    is_published = COALESCE($8, is_published),
                    category_id = COALESCE($9, category_id),
                    updated_at = NOW()
                WHERE id = $1
                RETURNING id, title, description, price, stock, brand, thumbnail_key, is_published, category_id;
                """,
                product_id,
                normalized_data["title"],
                normalized_data["description"],
                normalized_data["price"],
                normalized_data["stock"],
                normalized_data["brand"],
                normalized_data["thumbnail_key"],
                normalized_data["is_published"],
                normalized_data["category_id"],
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Category does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Product violates a unique constraint") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to update product") from exc

        if not row:
            raise RepositoryRecordNotFoundError(
                "Product not found",
            )

        return self._map_row(row)

    async def delete(self, product_id: int) -> Product:
        try:
            row = await self._conn.fetchrow("DELETE FROM products WHERE id = $1 RETURNING id, title, description, price, stock, brand, thumbnail_key, is_published, category_id;", product_id)
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Product is referenced by another entity") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete product") from exc

        if not row:
            raise RepositoryRecordNotFoundError("Product not found")

        return self._map_row(row)

    async def exists_product_with_id(self, product_id: int) -> bool:
        try:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM products WHERE id = $1) AS exists;",
                product_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to check product") from exc

        return row["exists"]

    @staticmethod
    def _normalize_update_data(
        data: ProductUpdateData,
    ) -> dict[str, str | int | bool | Decimal | None]:
        return {
            "title": data.title,
            "description": data.description,
            "price": data.price,
            "stock": data.stock,
            "brand": data.brand,
            "thumbnail_key": data.thumbnail_key,
            "is_published": data.is_published,
            "category_id": data.category_id,
        }

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
