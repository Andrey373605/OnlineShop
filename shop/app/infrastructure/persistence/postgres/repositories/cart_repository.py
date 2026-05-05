from uuid import UUID

from shop.app.domain.entities.cart import Cart
from shop.app.application.interfaces.repositories import CartRepository


class CartRepositorySql(CartRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[Cart]:
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
        return [self._map_cart(row) for row in rows]

    async def get_by_id(self, cart_id: UUID) -> Cart | None:
        row = await self._conn.fetchrow(
            """
            SELECT c.id, c.user_id, u.username, c.created_at, c.total_amount
            FROM carts c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.id = $1;
            """,
            cart_id,
        )
        return self._map_cart(row) if row else None

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        row = await self._conn.fetchrow(
            """
            SELECT c.id, c.user_id, c.created_at, c.total_amount
            FROM carts c
            WHERE c.user_id = $1;
            """,
            user_id,
        )
        return self._map_cart(row) if row else None

    async def add(self, cart: Cart) -> None:
        await self._conn.execute(
            """
            INSERT INTO carts (user_id, total_amount)
            VALUES ($1, COALESCE($2, 0.0));
            """,
            cart.user_id,
            cart.total_amount,
        )

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

    async def update(self, cart: Cart) -> None:
        await self._conn.execute(
            """
            UPDATE carts
            SET user_id = $2,
                total_amount = $3
            WHERE id = $1;
            """,
            cart.id,
            cart.user_id,
            cart.total_amount,
        )

    async def delete(self, cart_id: UUID) -> None:
        await self._conn.execute(
            "DELETE FROM carts WHERE id = $1;",
            cart_id,
        )

    @staticmethod
    def _map_cart(row) -> Cart:
        return Cart(
            id=row["id"],
            user_id=row["user_id"],
            items=[],
        )
