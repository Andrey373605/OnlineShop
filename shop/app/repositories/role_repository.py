from shop.app.schemas.role_schemas import RoleOut


class RoleRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_all(self) -> list[RoleOut]:
        rows = await self._queries.get_all_roles(self._conn)
        return [RoleOut(**row) for row in rows]

    async def get_by_id(self, role_id: int) -> RoleOut | None:
        row = await self._queries.get_role_by_id(self._conn, id=role_id)
        return RoleOut(**row) if row else None

    async def get_by_name(self, name: str) -> RoleOut | None:
        row = await self._queries.get_role_by_name(self._conn, name=name)
        return RoleOut(**row) if row else None

    async def create(self, name: str) -> int:
        result = await self._queries.create_role(self._conn, name=name)
        return result["id"]

    async def update(self, role_id: int, name: str) -> bool:
        result = await self._queries.update_role(self._conn, id=role_id, name=name)
        return bool(result)

    async def delete(self, role_id: int) -> bool:
        result = await self._queries.delete_role(self._conn, id=role_id)
        return bool(result)

    async def exists_with_name(self, name: str) -> bool:
        result = await self._queries.check_role_name_exists(self._conn, name=name)
        return result["exists"]


