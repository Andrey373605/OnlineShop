from shop.app.schemas.role_schemas import RoleOut


class RoleRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self) -> list[RoleOut]:
        rows = await self.queries.get_all_roles(self.conn)
        return [RoleOut(**row) for row in rows]

    async def get_by_id(self, role_id: int) -> RoleOut | None:
        row = await self.queries.get_role_by_id(self.conn, id=role_id)
        return RoleOut(**row) if row else None

    async def get_by_name(self, name: str) -> RoleOut | None:
        row = await self.queries.get_role_by_name(self.conn, name=name)
        return RoleOut(**row) if row else None

    async def create(self, name: str) -> int:
        result = await self.queries.create_role(self.conn, name=name)
        return result["id"]

    async def update(self, role_id: int, name: str) -> bool:
        result = await self.queries.update_role(self.conn, id=role_id, name=name)
        return bool(result)

    async def delete(self, role_id: int) -> bool:
        result = await self.queries.delete_role(self.conn, id=role_id)
        return bool(result)

    async def exists_with_name(self, name: str) -> bool:
        result = await self.queries.check_role_name_exists(self.conn, name=name)
        return result["exists"]


