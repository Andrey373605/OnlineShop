from shop.app.models.schemas import OrderOut
from shop.app.repositories.protocols import OrderRepository


class OrderRepositorySql(OrderRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[OrderOut]:
        rows = await self._conn.fetch(
            """
            SELECT o.id, o.user_id, u.username, o.order_number, o.status, o.total_amount,
                   o.shipping_address, o.payment_method, o.payment_status, o.created_at
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return [OrderOut(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self._conn.fetchrow("SELECT COUNT(*) AS total FROM orders;")
        return row["total"]

    async def get_by_id(self, order_id: int) -> OrderOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT o.id, o.user_id, o.order_number, o.status, o.total_amount,
                   o.shipping_address, o.payment_method, o.payment_status, o.created_at
            FROM orders o
            WHERE o.id = $1;
            """,
            order_id,
        )
        return OrderOut(**row) if row else None

    async def get_by_number(self, order_number: str) -> OrderOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT o.id, o.user_id, o.order_number, o.status, o.total_amount,
                   o.shipping_address, o.payment_method, o.payment_status, o.created_at
            FROM orders o
            WHERE o.order_number = $1;
            """,
            order_number,
        )
        return OrderOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO orders (
                user_id, order_number, status, total_amount, shipping_address, payment_method, payment_status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id;
            """,
            data.get("user_id"),
            data.get("order_number"),
            data.get("status"),
            data.get("total_amount"),
            data.get("shipping_address"),
            data.get("payment_method"),
            data.get("payment_status"),
        )
        return result["id"]

    async def update(self, order_id: int, data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE orders
            SET status = COALESCE($2, status),
                total_amount = COALESCE($3, total_amount),
                shipping_address = COALESCE($4, shipping_address),
                payment_method = COALESCE($5, payment_method),
                payment_status = COALESCE($6, payment_status)
            WHERE id = $1
            RETURNING id, status, total_amount;
            """,
            order_id,
            data.get("status"),
            data.get("total_amount"),
            data.get("shipping_address"),
            data.get("payment_method"),
            data.get("payment_status"),
        )
        return bool(result)

    async def delete(self, order_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM orders WHERE id = $1 RETURNING id;",
            order_id,
        )
        return bool(result)
