from uuid import UUID

from shop.app.domain.entities.permission import Permission
from shop.app.domain.entities.role import Role
from shop.app.application.interfaces.repositories import RoleRepository


class RoleRepositorySql(RoleRepository):
    def __init__(self, conn):
        self._conn = conn

    async def list_all(self) -> list[Role]:
        rows = await self._conn.fetch(
            """
            SELECT
                r.id AS role_id,
                r.name AS role_name,
                p.id AS permission_id,
                p.name AS permission_name
            FROM roles r
            LEFT JOIN role_permissions rp ON rp.role_id = r.id
            LEFT JOIN permissions p ON p.id = rp.permission_id
            ORDER BY r.id;
            """
        )
        return self._map_roles_with_permissions(rows)

    async def get_by_id(self, role_id: UUID) -> Role | None:
        row = await self._conn.fetchrow("SELECT id, name FROM roles WHERE id = $1;", role_id)
        return await self._hydrate_role(row) if row else None

    async def get_by_name(self, name: str) -> Role | None:
        row = await self._conn.fetchrow("SELECT id, name FROM roles WHERE name = $1;", name)
        return await self._hydrate_role(row) if row else None

    async def add(self, role: Role) -> None:
        await self._conn.execute(
            "INSERT INTO roles (name) VALUES ($1);",
            role.name,
        )

    async def create(self, name: str) -> int:
        result = await self._conn.fetchrow(
            "INSERT INTO roles (name) VALUES ($1) RETURNING id;",
            name,
        )
        return result["id"]

    async def update(self, role: Role) -> None:
        await self._conn.execute(
            "UPDATE roles SET name = $2 WHERE id = $1;",
            role.id,
            role.name,
        )

    async def delete(self, role_id: UUID) -> None:
        await self._conn.execute(
            "DELETE FROM roles WHERE id = $1;",
            role_id,
        )

    async def get_all(self) -> list[Role]:
        return await self.list_all()

    async def exists_with_name(self, name: str) -> bool:
        result = await self._conn.fetchrow(
            "SELECT EXISTS(SELECT 1 FROM roles WHERE name = $1) AS exists;",
            name,
        )
        return result["exists"]

    async def _hydrate_role(self, row) -> Role:
        permission_rows = await self._conn.fetch(
            """
            SELECT p.id, p.name
            FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.id
            WHERE rp.role_id = $1;
            """,
            row["id"],
        )
        permissions = {Permission(id=p["id"], name=p["name"]) for p in permission_rows}
        return Role(id=row["id"], name=row["name"], permissions=permissions)

    @staticmethod
    def _map_roles_with_permissions(rows) -> list[Role]:
        roles_map: dict[UUID, dict] = {}
        for row in rows:
            role_id = row["role_id"]
            role_name = row["role_name"]
            entry = roles_map.get(role_id)
            if entry is None:
                entry = {"name": role_name, "permissions": set()}
                roles_map[role_id] = entry
            permission_id = row["permission_id"]
            if permission_id is not None:
                entry["permissions"].add(Permission(id=permission_id, name=row["permission_name"]))
        return [
            Role(id=role_id, name=data["name"], permissions=data["permissions"])
            for role_id, data in roles_map.items()
        ]
