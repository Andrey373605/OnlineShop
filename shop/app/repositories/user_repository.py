from datetime import datetime

from shop.app.models.schemas import UserDB, UserOut


class UserRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_all(self, limit: int, offset: int) -> list[UserOut]:
        rows = await self._queries.get_all_users(
            self._conn,
            limit=limit,
            offset=offset,
        )
        return [UserOut(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self._queries.get_users_count(self._conn)
        return row["total"]

    async def get_by_id(self, user_id: int) -> UserOut | None:
        row = await self._queries.get_user_by_id(self._conn, id=user_id)
        return UserOut(**row) if row else None

    async def get_by_username(self, username: str) -> UserDB | None:
        row = await self._queries.get_user_by_username(
            self._conn,
            username=username,
        )
        return UserDB(**row) if row else None

    async def create(self, user_data: dict) -> int:
        result = await self._queries.create_user(self._conn, **user_data)
        return result["id"]

    async def update(self, user_id: int, update_data: dict) -> bool:
        result = await self._queries.update_user(
            self._conn,
            id=user_id,
            **update_data,
        )
        return bool(result)

    async def update_last_login(
        self, user_id: int, last_login: datetime | None = None
    ) -> bool:
        result = await self._queries.update_last_login(
            self._conn, id=user_id, last_login=last_login
        )
        return bool(result)

    async def delete(self, user_id: int) -> bool:
        result = await self._queries.delete_user(self._conn, id=user_id)
        return bool(result)

    async def exists_with_username(self, username: str) -> bool:
        row = await self._queries.check_user_username_exists(
            self._conn,
            username=username,
        )
        return row["exists"]

    async def exists_with_email(self, email: str) -> bool:
        row = await self._queries.check_user_email_exists(
            self._conn,
            email=email,
        )
        return row["exists"]
