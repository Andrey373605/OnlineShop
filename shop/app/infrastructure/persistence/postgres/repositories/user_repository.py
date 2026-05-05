from datetime import datetime
from uuid import UUID

from shop.app.domain.entities.user import User
from shop.app.application.interfaces.repositories import UserRepository


class UserRepositorySql(UserRepository):
    def __init__(self, conn):
        self._conn = conn

    async def list_paginated(self, limit: int, offset: int) -> list[User]:
        rows = await self._conn.fetch(
            """
            SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                   u.last_login, u.created_at, u.updated_at, u.password_hash
            FROM users u
            ORDER BY u.id
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return [self._map_user(row) for row in rows]

    async def get_total(self) -> int:
        row = await self._conn.fetchrow("SELECT COUNT(*) AS total FROM users;")
        return row["total"]

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self._conn.fetchrow(
            """
            SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                   u.last_login, u.created_at, u.updated_at, u.password_hash
            FROM users u
            WHERE u.id = $1;
            """,
            user_id,
        )
        return self._map_user(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        row = await self._conn.fetchrow(
            """
            SELECT id, username, email, full_name, is_active, last_login, created_at, updated_at, password_hash
            FROM users
            WHERE email = $1;
            """,
            email,
        )
        return self._map_user(row) if row else None

    async def get_by_username(self, username: str) -> User | None:
        row = await self._conn.fetchrow(
            """
            SELECT u.id, u.username, u.email, u.full_name, u.is_active,
                   u.last_login, u.created_at, u.updated_at, u.password_hash
            FROM users u
            WHERE u.username = $1;
            """,
            username,
        )
        return self._map_user(row) if row else None

    async def add(self, user: User) -> None:
        await self._conn.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, is_active, last_login)
            VALUES ($1, $2, $3, $4, $5, $6);
            """,
            user.username,
            user.email,
            user.password_hash,
            user.full_name,
            user.is_active,
            None,
        )

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

    async def update(self, user: User) -> None:
        await self._conn.execute(
            """
            UPDATE users
            SET username = $2,
                email = $3,
                password_hash = $4,
                full_name = $5,
                is_active = $6,
                updated_at = NOW()
            WHERE id = $1
            """,
            user.id,
            user.username,
            user.email,
            user.password_hash,
            user.full_name,
            user.is_active,
        )

    async def update_last_login(self, user_id: int, last_login: datetime | None = None) -> bool:
        result = await self._conn.execute(
            "UPDATE users SET last_login = $2, updated_at = NOW() WHERE id = $1;",
            user_id,
            last_login,
        )
        return result.endswith("1")

    async def delete(self, user_id: UUID) -> None:
        await self._conn.execute(
            "DELETE FROM users WHERE id = $1;",
            user_id,
        )

    async def exists_username(self, username: str, *, exclude_id: UUID | None = None) -> bool:
        if exclude_id is None:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1) AS exists;",
                username,
            )
        else:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1 AND id <> $2) AS exists;",
                username,
                exclude_id,
            )
        return bool(row["exists"])

    async def exists_email(self, email: str, *, exclude_id: UUID | None = None) -> bool:
        if exclude_id is None:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1) AS exists;",
                email,
            )
        else:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1 AND id <> $2) AS exists;",
                email,
                exclude_id,
            )
        return bool(row["exists"])

    # Backward-compatible aliases.
    async def get_all(self, limit: int, offset: int) -> list[User]:
        return await self.list_paginated(limit, offset)

    async def exists_with_username(self, username: str) -> bool:
        return await self.exists_username(username)

    async def exists_with_email(self, email: str) -> bool:
        return await self.exists_email(email)

    @staticmethod
    def _map_user(row) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            full_name=row["full_name"],
            password_hash=row["password_hash"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_login=row["last_login"],
        )
