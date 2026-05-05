from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import WarehouseRepository
from shop.app.domain.entities.warehouse import Warehouse


class WarehouseRepositorySql(WarehouseRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, warehouse_id: UUID) -> Warehouse | None:
        row = await self._conn.fetchrow(
            "SELECT id, name, address, is_active FROM warehouses WHERE id = $1;",
            warehouse_id,
        )
        return self._map_row(row) if row else None

    async def list_all(self) -> list[Warehouse]:
        rows = await self._conn.fetch(
            "SELECT id, name, address, is_active FROM warehouses ORDER BY name;"
        )
        return [self._map_row(row) for row in rows]

    async def add(self, warehouse: Warehouse) -> None:
        await self._conn.execute(
            """
            INSERT INTO warehouses (id, name, address, is_active)
            VALUES ($1, $2, $3, $4);
            """,
            warehouse.id,
            warehouse.name,
            warehouse.address,
            warehouse.is_active,
        )

    async def update(self, warehouse: Warehouse) -> None:
        await self._conn.execute(
            """
            UPDATE warehouses
            SET name = $2, address = $3, is_active = $4
            WHERE id = $1;
            """,
            warehouse.id,
            warehouse.name,
            warehouse.address,
            warehouse.is_active,
        )

    async def delete(self, warehouse_id: UUID) -> None:
        await self._conn.execute("DELETE FROM warehouses WHERE id = $1;", warehouse_id)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> Warehouse:
        return Warehouse(
            id=row["id"],
            name=row["name"],
            address=row["address"],
            is_active=row["is_active"],
        )
