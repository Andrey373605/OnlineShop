from datetime import datetime

from shop.app.models.schemas import UserDB, UserOut
from shop.app.repositories.protocols import UserRepository


class UserRepositorySql(UserRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[UserOut]:
        rows = await self._conn.fetch(
            """
            SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                   u.role AS role_id, r.name AS role_name, u.last_login, u.created_at, u.updated_at
            FROM users u
            LEFT JOIN roles r ON u.role = r.id
            ORDER BY u.id
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return [UserOut(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self._conn.fetchrow("SELECT COUNT(*) AS total FROM users;")
        return row["total"]

    async def get_by_id(self, user_id: int) -> UserOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                   u.role AS role_id, r.name AS role_name, u.last_login, u.created_at, u.updated_at
            FROM users u
            LEFT JOIN roles r ON u.role = r.id
            WHERE u.id = $1;
            """,
            user_id,
        )
        return UserOut(**row) if row else None

    async def get_by_username(self, username: str) -> UserDB | None:
        row = await self._conn.fetchrow(
            """
            SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                   u.role AS role_id, r.name AS role_name, u.last_login, u.created_at, u.updated_at,
                   u.password_hash
            FROM users u
            LEFT JOIN roles r ON u.role = r.id
            WHERE u.username = $1;
            """,
            username,
        )
        return UserDB(**row) if row else None

    async def create(self, user_data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO users (username, email, password_hash, full_name, is_active, role, last_login)
            VALUES ($1, $2, $3, $4, COALESCE($5, TRUE), $6, $7)
            RETURNING id;
            """,
            user_data.get("username"),
            user_data.get("email"),
            user_data.get("password_hash"),
            user_data.get("full_name"),
            user_data.get("is_active"),
            user_data.get("role"),
            user_data.get("last_login"),
        )
        return result["id"]

    async def update(self, user_id: int, update_data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE users
            SET username = COALESCE($2, username),
                email = COALESCE($3, email),
                password_hash = COALESCE($4, password_hash),
                full_name = COALESCE($5, full_name),
                is_active = COALESCE($6, is_active),
                role = COALESCE($7, role),
                last_login = COALESCE($8, last_login),
                updated_at = NOW()
            WHERE id = $1
            RETURNING id;
            """,
            user_id,
            update_data.get("username"),
            update_data.get("email"),
            update_data.get("password_hash"),
            update_data.get("full_name"),
            update_data.get("is_active"),
            update_data.get("role"),
            update_data.get("last_login"),
        )
        return bool(result)

    async def update_last_login(
        self, user_id: int, last_login: datetime | None = None
    ) -> bool:
        result = await self._conn.execute(
            "UPDATE users SET last_login = $2, updated_at = NOW() WHERE id = $1;",
            user_id,
            last_login,
        )
        return result.endswith("1")

    async def delete(self, user_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM users WHERE id = $1 RETURNING id;",
            user_id,
        )
        return bool(result)

    async def exists_with_username(self, username: str) -> bool:
        row = await self._conn.fetchrow(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1) AS exists;",
            username,
        )
        return row["exists"]

    async def exists_with_email(self, email: str) -> bool:
        row = await self._conn.fetchrow(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1) AS exists;",
            email,
        )
        return row["exists"]
