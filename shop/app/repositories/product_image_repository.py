from typing import Any, Mapping

import asyncpg

from shop.app.models.domain.product_image import (
    ProductImageCreateData,
    ProductImage,
    ProductImageUpdateData,
)
from shop.app.repositories.exceptions import (
    RepositoryRecordNotFoundError,
    RepositoryUnavailableError,
    RepositoryMappingError,
    RepositoryUnexpectedResultError,
    RepositoryForeignKeyError,
    RepositoryUniqueConstraintError,
)


class ProductImageRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_product_id(self, product_id: int) -> list[ProductImage]:
        try:
            rows = await self._queries.get_product_images_by_product_id(
                self._conn,
                product_id=product_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch product image") from exc

        return [self._map_row(row) for row in rows]

    async def get_by_id(self, image_id: int) -> ProductImage:
        try:
            row = await self._queries.get_product_image_by_id(self._conn, id=image_id)
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch product image") from exc

        if not row:
            raise RepositoryRecordNotFoundError(
                "Product image not found",
            )

        return self._map_row(row)

    async def create(self, image_data: ProductImageCreateData) -> ProductImage:
        try:
            row = await self._queries.create_product_image(
                self._conn,
                product_id=image_data.product_id,
                storage_key=image_data.storage_key,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Product does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError(
                "Product image with this product_id and storage_key already exists"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to create product image") from exc

        if not row:
            raise RepositoryUnexpectedResultError("Database did not return created product image")

        return self._map_row(row)

    async def update(self, image_id: int, image_data: ProductImageUpdateData) -> ProductImage:
        normalized_data = self._normalize_update_data(image_data)

        try:
            row = await self._queries.update_product_image(
                self._conn,
                id=image_id,
                **normalized_data,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Product does not exist") from exc
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError(
                "Product image with this product_id and storage_key already exists"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to update product image") from exc

        if not row:
            raise RepositoryRecordNotFoundError(
                "Product image not found",
            )

        return self._map_row(row)

    async def delete(self, image_id: int) -> None:
        try:
            row = await self._queries.delete_product_image(self._conn, id=image_id)
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError(
                "Product image is referenced by another entity"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete product image") from exc

        if not row:
            raise RepositoryRecordNotFoundError("Product image not found")

    async def delete_by_product_id(self, product_id: int) -> list[int]:
        try:
            rows = await self._queries.delete_product_images_by_product_id(
                self._conn,
                product_id=product_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError(
                "Product images are referenced by another entity"
            ) from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete product images") from exc

        return [row["id"] for row in rows]

    @staticmethod
    def _normalize_update_data(data: ProductImageUpdateData) -> dict[str, int | str | None]:
        return {
            "product_id": data.product_id,
            "storage_key": data.storage_key,
        }

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
