from shop.app.models.schemas import OrderItemOut
from shop.app.repositories.protocols import OrderItemRepository


class OrderItemRepositorySql(OrderItemRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_order_id(self, order_id: int) -> list[OrderItemOut]:
        rows = await self._conn.fetch(
            """
            SELECT oi.id, oi.order_id, oi.product_id, p.title AS product_title, oi.quantity, oi.unit_price
            FROM orders_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = $1
            ORDER BY oi.id;
            """,
            order_id,
        )
        return [OrderItemOut(**row) for row in rows]

    async def get_by_id(self, item_id: int) -> OrderItemOut | None:
        row = await self._conn.fetchrow(
            "SELECT id, order_id, product_id, quantity, unit_price FROM orders_items WHERE id = $1;",
            item_id,
        )
        return OrderItemOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO orders_items (order_id, product_id, quantity, unit_price)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
            """,
            data.get("order_id"),
            data.get("product_id"),
            data.get("quantity"),
            data.get("unit_price"),
        )
        return result["id"]

    async def update(self, item_id: int, data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE orders_items
            SET order_id = COALESCE($2, order_id),
                product_id = COALESCE($3, product_id),
                quantity = COALESCE($4, quantity),
                unit_price = COALESCE($5, unit_price)
            WHERE id = $1
            RETURNING id, order_id, product_id, quantity, unit_price;
            """,
            item_id,
            data.get("order_id"),
            data.get("product_id"),
            data.get("quantity"),
            data.get("unit_price"),
        )
        return bool(result)

    async def delete(self, item_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM orders_items WHERE id = $1 RETURNING id;",
            item_id,
        )
        return bool(result)

    async def delete_by_order_id(self, order_id: int):
        rows = await self._conn.fetch(
            "DELETE FROM orders_items WHERE order_id = $1 RETURNING id;",
            order_id,
        )
        return [row["id"] for row in rows]
