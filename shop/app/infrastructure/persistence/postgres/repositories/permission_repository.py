from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import PermissionRepository
from shop.app.domain.entities.permission import Permission


class PermissionRepositorySql(PermissionRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        row = await self._conn.fetchrow(
            "SELECT id, name FROM permissions WHERE id = $1;",
            permission_id,
        )
        return self._map_row(row) if row else None

    async def get_by_name(self, name: str) -> Permission | None:
        row = await self._conn.fetchrow(
            "SELECT id, name FROM permissions WHERE name = $1;",
            name,
        )
        return self._map_row(row) if row else None

    async def list_all(self) -> list[Permission]:
        rows = await self._conn.fetch("SELECT id, name FROM permissions ORDER BY name;")
        return [self._map_row(row) for row in rows]

    async def add(self, permission: Permission) -> None:
        await self._conn.execute(
            "INSERT INTO permissions (id, name) VALUES ($1, $2);",
            permission.id,
            permission.name,
        )

    async def update(self, permission: Permission) -> None:
        await self._conn.execute(
            "UPDATE permissions SET name = $2 WHERE id = $1;",
            permission.id,
            permission.name,
        )

    async def delete(self, permission_id: UUID) -> None:
        await self._conn.execute("DELETE FROM permissions WHERE id = $1;", permission_id)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> Permission:
        return Permission(
            id=row["id"],
            name=row["name"],
        )
