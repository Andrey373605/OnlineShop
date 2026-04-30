from shop.app.models.schemas import (
    ProductSpecificationOut,
)
from shop.app.repositories.protocols import ProductSpecificationRepository


class ProductSpecificationRepositorySql(ProductSpecificationRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self) -> list[ProductSpecificationOut]:
        rows = await self._conn.fetch(
            """
            SELECT id, product_id, specifications, created_at, updated_at
            FROM product_specifications
            ORDER BY id;
            """
        )
        return [ProductSpecificationOut(**row) for row in rows]

    async def get_by_id(self, specification_id: int) -> ProductSpecificationOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT id, product_id, specifications, created_at, updated_at
            FROM product_specifications
            WHERE id = $1;
            """,
            specification_id,
        )
        return ProductSpecificationOut(**row) if row else None

    async def get_by_product_id(
        self, product_id: int
    ) -> ProductSpecificationOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT id, product_id, specifications, created_at, updated_at
            FROM product_specifications
            WHERE product_id = $1;
            """,
            product_id,
        )
        return ProductSpecificationOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO product_specifications (product_id, specifications)
            VALUES ($1, COALESCE($2::jsonb, '{}'::jsonb))
            RETURNING id;
            """,
            data.get("product_id"),
            data.get("specifications"),
        )
        return result["id"]

    async def update(self, specification_id: int, data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE product_specifications
            SET product_id = COALESCE($2, product_id),
                specifications = COALESCE($3::jsonb, specifications),
                updated_at = NOW()
            WHERE id = $1
            RETURNING id, product_id, specifications;
            """,
            specification_id,
            data.get("product_id"),
            data.get("specifications"),
        )
        return bool(result)

    async def delete(self, specification_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM product_specifications WHERE id = $1 RETURNING id;",
            specification_id,
        )
        return bool(result)
