from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import ProductVariantDetailsRepository
from shop.app.domain.entities.product_variant_details import ProductVariantDetails


class ProductVariantDetailsRepositorySql(ProductVariantDetailsRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, details_id: UUID) -> ProductVariantDetails | None:
        row = await self._conn.fetchrow(
            "SELECT id, variant_id, attributes FROM product_variant_details WHERE id = $1;",
            details_id,
        )
        return self._map_row(row) if row else None

    async def get_by_variant_id(self, variant_id: UUID) -> ProductVariantDetails | None:
        row = await self._conn.fetchrow(
            "SELECT id, variant_id, attributes FROM product_variant_details WHERE variant_id = $1;",
            variant_id,
        )
        return self._map_row(row) if row else None

    async def add(self, details: ProductVariantDetails) -> None:
        await self._conn.execute(
            """
            INSERT INTO product_variant_details (id, variant_id, attributes)
            VALUES ($1, $2, $3::jsonb);
            """,
            details.id,
            details.variant_id,
            details.attributes,
        )

    async def update(self, details: ProductVariantDetails) -> None:
        await self._conn.execute(
            """
            UPDATE product_variant_details
            SET variant_id = $2, attributes = $3::jsonb
            WHERE id = $1;
            """,
            details.id,
            details.variant_id,
            details.attributes,
        )

    async def delete(self, details_id: UUID) -> None:
        await self._conn.execute(
            "DELETE FROM product_variant_details WHERE id = $1;",
            details_id,
        )

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> ProductVariantDetails:
        return ProductVariantDetails(
            id=row["id"],
            variant_id=row["variant_id"],
            attributes=row["attributes"],
        )
