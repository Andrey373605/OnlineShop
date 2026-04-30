from shop.app.models.schemas import RoleOut
from shop.app.repositories.protocols import RoleRepository


class RoleRepositorySql(RoleRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self) -> list[RoleOut]:
        rows = await self._conn.fetch("SELECT id, name FROM roles ORDER BY id;")
        return [RoleOut(**row) for row in rows]

    async def get_by_id(self, role_id: int) -> RoleOut | None:
        row = await self._conn.fetchrow("SELECT id, name FROM roles WHERE id = $1;", role_id)
        return RoleOut(**row) if row else None

    async def get_by_name(self, name: str) -> RoleOut | None:
        row = await self._conn.fetchrow("SELECT id, name FROM roles WHERE name = $1;", name)
        return RoleOut(**row) if row else None

    async def create(self, name: str) -> int:
        result = await self._conn.fetchrow(
            "INSERT INTO roles (name) VALUES ($1) RETURNING id;",
            name,
        )
        return result["id"]

    async def update(self, role_id: int, name: str) -> bool:
        result = await self._conn.fetchrow(
            "UPDATE roles SET name = $2 WHERE id = $1 RETURNING id, name;",
            role_id,
            name,
        )
        return bool(result)

    async def delete(self, role_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM roles WHERE id = $1 RETURNING id;",
            role_id,
        )
        return bool(result)

    async def exists_with_name(self, name: str) -> bool:
        result = await self._conn.fetchrow(
            "SELECT EXISTS(SELECT 1 FROM roles WHERE name = $1) AS exists;",
            name,
        )
        return result["exists"]
