from decimal import Decimal
from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import ProductVariantRepository
from shop.app.domain.value_objects.price import Price
from shop.app.domain.entities.product_variant import ProductVariant


class ProductVariantRepositorySql(ProductVariantRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, variant_id: UUID) -> ProductVariant | None:
        row = await self._conn.fetchrow(
            "SELECT id, product_id, sku, price, display_name FROM product_variants WHERE id = $1;",
            variant_id,
        )
        return self._map_row(row) if row else None

    async def get_by_sku(self, sku: str) -> ProductVariant | None:
        row = await self._conn.fetchrow(
            "SELECT id, product_id, sku, price, display_name FROM product_variants WHERE sku = $1;",
            sku,
        )
        return self._map_row(row) if row else None

    async def list_by_product_id(self, product_id: UUID) -> list[ProductVariant]:
        rows = await self._conn.fetch(
            "SELECT id, product_id, sku, price, display_name FROM product_variants WHERE product_id = $1 ORDER BY id;",
            product_id,
        )
        return [self._map_row(row) for row in rows]

    async def add(self, variant: ProductVariant) -> None:
        await self._conn.execute(
            """
            INSERT INTO product_variants (id, product_id, sku, price, display_name)
            VALUES ($1, $2, $3, $4, $5);
            """,
            variant.id,
            variant.product_id,
            variant.sku,
            variant.price.amount,
            variant.display_name,
        )

    async def update(self, variant: ProductVariant) -> None:
        await self._conn.execute(
            """
            UPDATE product_variants
            SET product_id = $2, sku = $3, price = $4, display_name = $5
            WHERE id = $1;
            """,
            variant.id,
            variant.product_id,
            variant.sku,
            variant.price.amount,
            variant.display_name,
        )

    async def delete(self, variant_id: UUID) -> None:
        await self._conn.execute("DELETE FROM product_variants WHERE id = $1;", variant_id)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> ProductVariant:
        raw_price = row["price"]
        amount = raw_price if isinstance(raw_price, Decimal) else Decimal(str(raw_price))
        return ProductVariant(
            id=row["id"],
            product_id=row["product_id"],
            sku=row["sku"],
            price=Price(amount, "USD"),
            display_name=row["display_name"],
        )
