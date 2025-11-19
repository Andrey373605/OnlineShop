from shop.app.schemas.refresh_token_schemas import RefreshTokenOut


class RefreshTokenRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_by_user_id(self, user_id: int) -> list[RefreshTokenOut]:
        rows = await self.queries.get_refresh_tokens_by_user_id(
            self.conn,
            user_id=user_id,
        )
        return [RefreshTokenOut(**row) for row in rows]

    async def get_by_hash(self, token_hash: str) -> RefreshTokenOut | None:
        row = await self.queries.get_refresh_token_by_hash(
            self.conn,
            token_hash=token_hash,
        )
        return RefreshTokenOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_refresh_token(self.conn, **data)
        return result["id"]

    async def delete(self, token_id: int) -> bool:
        result = await self.queries.delete_refresh_token(self.conn, id=token_id)
        return bool(result)

    async def delete_by_hash(self, token_hash: str):
        rows = await self.queries.delete_refresh_token_by_hash(
            self.conn,
            token_hash=token_hash,
        )
        return [row["id"] for row in rows]

    async def delete_by_user_id(self, user_id: int):
        rows = await self.queries.delete_refresh_tokens_by_user_id(
            self.conn,
            user_id=user_id,
        )
        return [row["id"] for row in rows]


