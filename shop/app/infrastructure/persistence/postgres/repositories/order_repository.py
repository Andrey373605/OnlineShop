from decimal import Decimal
from uuid import UUID

from shop.app.domain.entities.order import Order, OrderItem, OrderStatus, PaymentStatus
from shop.app.domain.value_objects.price import Price
from shop.app.application.interfaces.repositories import OrderRepository


class OrderRepositorySql(OrderRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[Order]:
        rows = await self._conn.fetch(
            """
            SELECT
                o.id AS order_id,
                o.user_id,
                o.order_number,
                o.status,
                o.total_amount,
                o.shipping_address,
                o.payment_method,
                o.payment_status,
                o.created_at,
                oi.id AS item_id,
                oi.product_id,
                oi.quantity,
                oi.unit_price
            FROM orders o
            LEFT JOIN orders_items oi ON oi.order_id = o.id
            ORDER BY o.created_at DESC, oi.id
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return self._map_orders(rows)

    async def get_total(self) -> int:
        row = await self._conn.fetchrow("SELECT COUNT(*) AS total FROM orders;")
        return row["total"]

    async def get_by_id(self, order_id: UUID) -> Order | None:
        row = await self._conn.fetchrow(
            """
            SELECT o.id, o.user_id, o.order_number, o.status, o.total_amount,
                   o.shipping_address, o.payment_method, o.payment_status, o.created_at
            FROM orders o
            WHERE o.id = $1;
            """,
            order_id,
        )
        if not row:
            return None
        return await self._map_order(row)

    async def get_by_order_number(self, order_number: str) -> Order | None:
        row = await self._conn.fetchrow(
            """
            SELECT o.id, o.user_id, o.order_number, o.status, o.total_amount,
                   o.shipping_address, o.payment_method, o.payment_status, o.created_at
            FROM orders o
            WHERE o.order_number = $1;
            """,
            order_number,
        )
        if not row:
            return None
        return await self._map_order(row)

    async def list_for_user(self, user_id: UUID, limit: int, offset: int) -> list[Order]:
        rows = await self._conn.fetch(
            """
            SELECT
                o.id AS order_id,
                o.user_id,
                o.order_number,
                o.status,
                o.total_amount,
                o.shipping_address,
                o.payment_method,
                o.payment_status,
                o.created_at,
                oi.id AS item_id,
                oi.product_id,
                oi.quantity,
                oi.unit_price
            FROM orders o
            LEFT JOIN orders_items oi ON oi.order_id = o.id
            WHERE o.user_id = $1
            ORDER BY o.created_at DESC, oi.id
            LIMIT $2 OFFSET $3;
            """,
            user_id,
            limit,
            offset,
        )
        return self._map_orders(rows)

    async def list_paginated(self, limit: int, offset: int) -> list[Order]:
        return await self.get_all(limit, offset)

    async def add(self, order: Order) -> None:
        await self._conn.execute(
            """
            INSERT INTO orders (
                user_id, order_number, status, total_amount, shipping_address, payment_method, payment_status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7);
            """,
            order.user_id,
            order.order_number,
            order.status.value,
            order.total_price.amount,
            order.shipping_address,
            order.payment_method,
            order.payment_status.value,
        )

    async def update(self, order: Order) -> None:
        await self._conn.execute(
            """
            UPDATE orders
            SET status = $2,
                total_amount = $3,
                shipping_address = $4,
                payment_method = $5,
                payment_status = $6
            WHERE id = $1
            """,
            order.id,
            order.status.value,
            order.total_price.amount,
            order.shipping_address,
            order.payment_method,
            order.payment_status.value,
        )

    async def delete(self, order_id: UUID) -> None:
        await self._conn.execute(
            "DELETE FROM orders WHERE id = $1;",
            order_id,
        )

    # Backward-compatible aliases.
    async def get_by_number(self, order_number: str) -> Order | None:
        return await self.get_by_order_number(order_number)

    async def create(self, data: dict) -> UUID:
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

    async def _map_order(self, row) -> Order | None:
        item_rows = await self._conn.fetch(
            """
            SELECT id, order_id, product_id, quantity, unit_price
            FROM orders_items
            WHERE order_id = $1
            ORDER BY id;
            """,
            row["id"],
        )
        items = [
            OrderItem(
                id=item["id"],
                order_id=item["order_id"],
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=Price(Decimal(str(item["unit_price"])), "USD"),
            )
            for item in item_rows
        ]
        if not items:
            return None
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            order_number=row["order_number"],
            status=OrderStatus(str(row["status"])),
            payment_status=PaymentStatus(str(row["payment_status"])),
            shipping_address=row["shipping_address"] or "n/a",
            payment_method=row["payment_method"] or "n/a",
            items=items,
            created_at=row["created_at"],
        )

    @staticmethod
    def _map_orders(rows) -> list[Order]:
        grouped: dict[UUID, dict] = {}
        for row in rows:
            order_id = row["order_id"]
            entry = grouped.get(order_id)
            if entry is None:
                entry = {
                    "user_id": row["user_id"],
                    "order_number": row["order_number"],
                    "status": row["status"],
                    "payment_status": row["payment_status"],
                    "shipping_address": row["shipping_address"],
                    "payment_method": row["payment_method"],
                    "created_at": row["created_at"],
                    "items": [],
                }
                grouped[order_id] = entry
            if row["item_id"] is not None:
                entry["items"].append(
                    OrderItem(
                        id=row["item_id"],
                        order_id=order_id,
                        product_id=row["product_id"],
                        quantity=row["quantity"],
                        unit_price=Price(Decimal(str(row["unit_price"])), "USD"),
                    )
                )

        result: list[Order] = []
        for order_id, data in grouped.items():
            if not data["items"]:
                continue
            result.append(
                Order(
                    id=order_id,
                    user_id=data["user_id"],
                    order_number=data["order_number"],
                    status=OrderStatus(str(data["status"])),
                    payment_status=PaymentStatus(str(data["payment_status"])),
                    shipping_address=data["shipping_address"] or "n/a",
                    payment_method=data["payment_method"] or "n/a",
                    items=data["items"],
                    created_at=data["created_at"],
                )
            )
        return result
