from shop.app.models.schemas import CartOut
from shop.app.repositories.protocols import CartRepository


class CartRepositorySql(CartRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[CartOut]:
        rows = await self._conn.fetch(
            """
            SELECT c.id, c.user_id, u.username, c.created_at, c.total_amount
            FROM carts c
            LEFT JOIN users u ON c.user_id = u.id
            ORDER BY c.id
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return [CartOut(**row) for row in rows]

    async def get_by_id(self, cart_id: int) -> CartOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT c.id, c.user_id, u.username, c.created_at, c.total_amount
            FROM carts c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.id = $1;
            """,
            cart_id,
        )
        return CartOut(**row) if row else None

    async def get_by_user_id(self, user_id: int) -> CartOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT c.id, c.user_id, c.created_at, c.total_amount
            FROM carts c
            WHERE c.user_id = $1;
            """,
            user_id,
        )
        return CartOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO carts (user_id, total_amount)
            VALUES ($1, COALESCE($2, 0.0))
            RETURNING id;
            """,
            data.get("user_id"),
            data.get("total_amount"),
        )
        return result["id"]

    async def update(self, cart_id: int, data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE carts
            SET user_id = COALESCE($2, user_id),
                total_amount = COALESCE($3, total_amount)
            WHERE id = $1
            RETURNING id, user_id, total_amount;
            """,
            cart_id,
            data.get("user_id"),
            data.get("total_amount"),
        )
        return bool(result)

    async def delete(self, cart_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM carts WHERE id = $1 RETURNING id;",
            cart_id,
        )
        return bool(result)
