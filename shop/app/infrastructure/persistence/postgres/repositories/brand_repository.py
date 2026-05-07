from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import BrandRepository
from shop.app.domain import Brand


class BrandRepositorySql(BrandRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, brand_id: UUID) -> Brand | None:
        row = await self._conn.fetchrow(
            "SELECT id, name, description, logo_image_id FROM brands WHERE id = $1;",
            brand_id,
        )
        return self._map_row(row) if row else None

    async def list_all(self) -> list[Brand]:
        rows = await self._conn.fetch(
            "SELECT id, name, description, logo_image_id FROM brands ORDER BY name;"
        )
        return [self._map_row(row) for row in rows]

    async def add(self, brand: Brand) -> None:
        await self._conn.execute(
            """
            INSERT INTO brands (id, name, description, logo_image_id)
            VALUES ($1, $2, $3, $4);
            """,
            brand.id,
            brand.name,
            brand.description,
            brand.logo_image_id,
        )

    async def update(self, brand: Brand) -> None:
        await self._conn.execute(
            """
            UPDATE brands
            SET name = $2,
                description = $3,
                logo_image_id = $4
            WHERE id = $1;
            """,
            brand.id,
            brand.name,
            brand.description,
            brand.logo_image_id,
        )

    async def delete(self, brand_id: UUID) -> None:
        await self._conn.execute("DELETE FROM brands WHERE id = $1;", brand_id)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> Brand:
        return Brand(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            logo_image_id=row["logo_image_id"],
        )
