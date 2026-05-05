from typing import Any, Mapping
from uuid import UUID

import asyncpg

from shop.app.domain.entities.product_image import (
    ProductImage,
)
from shop.app.infrastructure.persistence.postgres.repositories.exceptions import (
    RepositoryUnavailableError,
    RepositoryMappingError,
    RepositoryUnexpectedResultError,
    RepositoryForeignKeyError,
    RepositoryUniqueConstraintError,
)
from shop.app.application.interfaces.repositories import ProductImageRepository


class ProductImageRepositorySql(ProductImageRepository):
    def __init__(self, conn):
        self._conn = conn

    async def list_by_product_id(self, product_id: UUID) -> list[ProductImage]:
        try:
            rows = await self._conn.fetch(
                """
                SELECT id, product_id, storage_key
                FROM product_images
                WHERE product_id = $1
                ORDER BY id;
                """,
                product_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch product image") from exc

        return [self._map_row(row) for row in rows]

    async def get_by_id(self, image_id: UUID) -> ProductImage | None:
        try:
            row = await self._conn.fetchrow(
                "SELECT id, product_id, storage_key FROM product_images WHERE id = $1;",
                image_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch product image") from exc

        return self._map_row(row) if row else None

    async def add(self, image: ProductImage) -> None:
        try:
            await self._conn.execute(
                """
                INSERT INTO product_images (product_id, storage_key)
                VALUES ($1, $2)
                """,
                image.product_id,
                image.storage_key,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Product does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError(
                "Product image with this product_id and storage_key already exists"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to create product image") from exc

    async def update(self, image: ProductImage) -> None:
        try:
            await self._conn.execute(
                """
                UPDATE product_images
                SET product_id = $2,
                    storage_key = $3
                WHERE id = $1
                """,
                image.id,
                image.product_id,
                image.storage_key,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Product does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError(
                "Product image with this product_id and storage_key already exists"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to update product image") from exc

    async def delete(self, image_id: UUID) -> None:
        try:
            await self._conn.execute(
                "DELETE FROM product_images WHERE id = $1;",
                image_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError(
                "Product image is referenced by another entity"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete product image") from exc

    async def delete_all_for_product(self, product_id: UUID) -> list[UUID]:
        try:
            rows = await self._conn.fetch(
                """
                DELETE FROM product_images
                WHERE product_id = $1
                RETURNING id, product_id, storage_key;
                """,
                product_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError(
                "Product images are referenced by another entity"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete product images") from exc

        return [row["id"] for row in rows]

    # Backward-compatible aliases.
    async def get_by_product_id(self, product_id: UUID) -> list[ProductImage]:
        return await self.list_by_product_id(product_id)

    async def create(self, image_data: ProductImage) -> ProductImage:
        await self.add(image_data)
        row = await self._conn.fetchrow(
            """
            SELECT id, product_id, storage_key
            FROM product_images
            WHERE product_id = $1 AND storage_key = $2
            ORDER BY id DESC
            LIMIT 1;
            """,
            image_data.product_id,
            image_data.storage_key,
        )
        if not row:
            raise RepositoryUnexpectedResultError("Database did not return created product image")
        return self._map_row(row)

    async def delete_by_product_id(self, product_id: UUID) -> list[UUID]:
        return await self.delete_all_for_product(product_id)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> ProductImage:
        try:
            return ProductImage(
                id=row["id"],
                product_id=row["product_id"],
                storage_key=row["storage_key"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RepositoryMappingError("Product image row has invalid shape") from exc
