from shop.app.schemas.user_schemas import UserOut


class UserRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self, limit: int, offset: int) -> list[UserOut]:
        rows = await self.queries.get_all_users(
            self.conn,
            limit=limit,
            offset=offset,
        )
        return [UserOut(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self.queries.get_users_count(self.conn)
        return row["total"]

    async def get_by_id(self, user_id: int) -> UserOut | None:
        row = await self.queries.get_user_by_id(self.conn, id=user_id)
        return UserOut(**row) if row else None

    async def get_by_username(self, username: str) -> UserOut | None:
        row = await self.queries.get_user_by_username(
            self.conn,
            username=username,
        )
        return UserOut(**row) if row else None

    async def create(self, user_data: dict) -> int:
        result = await self.queries.create_user(self.conn, **user_data)
        return result["id"]

    async def update(self, user_id: int, update_data: dict) -> bool:
        result = await self.queries.update_user(
            self.conn,
            id=user_id,
            **update_data,
        )
        return bool(result)

    async def delete(self, user_id: int) -> bool:
        result = await self.queries.delete_user(self.conn, id=user_id)
        return bool(result)

    async def exists_with_username(self, username: str) -> bool:
        row = await self.queries.check_user_username_exists(
            self.conn,
            username=username,
        )
        return row["exists"]

    async def exists_with_email(self, email: str) -> bool:
        row = await self.queries.check_user_email_exists(
            self.conn,
            email=email,
        )
        return row["exists"]


