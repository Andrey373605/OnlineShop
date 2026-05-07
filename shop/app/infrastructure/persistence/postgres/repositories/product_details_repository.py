from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import ProductDetailsRepository
from shop.app.domain.entities.product_details import ProductDetails


class ProductDetailsRepositorySql(ProductDetailsRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, details_id: UUID) -> ProductDetails | None:
        row = await self._conn.fetchrow(
            "SELECT id, product_id, attributes FROM product_details WHERE id = $1;",
            details_id,
        )
        return self._map_row(row) if row else None

    async def get_by_product_id(self, product_id: UUID) -> ProductDetails | None:
        row = await self._conn.fetchrow(
            "SELECT id, product_id, attributes FROM product_details WHERE product_id = $1;",
            product_id,
        )
        return self._map_row(row) if row else None

    async def add(self, details: ProductDetails) -> None:
        await self._conn.execute(
            "INSERT INTO product_details (id, product_id, attributes) VALUES ($1, $2, $3::jsonb);",
            details.id,
            details.product_id,
            details.attributes,
        )

    async def update(self, details: ProductDetails) -> None:
        await self._conn.execute(
            "UPDATE product_details SET product_id = $2, attributes = $3::jsonb WHERE id = $1;",
            details.id,
            details.product_id,
            details.attributes,
        )

    async def delete(self, details_id: UUID) -> None:
        await self._conn.execute("DELETE FROM product_details WHERE id = $1;", details_id)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> ProductDetails:
        return ProductDetails(
            id=row["id"],
            product_id=row["product_id"],
            attributes=row["attributes"],
        )
