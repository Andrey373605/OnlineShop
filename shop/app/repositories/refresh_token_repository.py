from shop.app.models.schemas import RefreshTokenOut
from shop.app.repositories.protocols import RefreshTokenRepository


class RefreshTokenRepositorySql(RefreshTokenRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_user_id(self, user_id: int) -> list[RefreshTokenOut]:
        rows = await self._conn.fetch(
            """
            SELECT id, user_id, token_hash, created_at, expires_at
            FROM refresh_tokens
            WHERE user_id = $1
            ORDER BY created_at DESC;
            """,
            user_id,
        )
        return [RefreshTokenOut(**row) for row in rows]

    async def get_by_hash(self, token_hash: str) -> RefreshTokenOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT id, user_id, token_hash, created_at, expires_at
            FROM refresh_tokens
            WHERE token_hash = $1;
            """,
            token_hash,
        )
        return RefreshTokenOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            RETURNING id;
            """,
            data.get("user_id"),
            data.get("token_hash"),
            data.get("expires_at"),
        )
        return result["id"]

    async def delete(self, token_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM refresh_tokens WHERE id = $1 RETURNING id;",
            token_id,
        )
        return bool(result)

    async def delete_by_hash(self, token_hash: str):
        rows = await self._conn.fetch(
            "DELETE FROM refresh_tokens WHERE token_hash = $1 RETURNING id;",
            token_hash,
        )
        return [row["id"] for row in rows]

    async def delete_by_user_id(self, user_id: int):
        rows = await self._conn.fetch(
            "DELETE FROM refresh_tokens WHERE user_id = $1 RETURNING id;",
            user_id,
        )
        return [row["id"] for row in rows]
