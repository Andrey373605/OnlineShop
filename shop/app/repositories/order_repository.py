from shop.app.schemas.order_schemas import OrderOut


class OrderRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self, limit: int, offset: int) -> list[OrderOut]:
        rows = await self.queries.get_all_orders(
            self.conn,
            limit=limit,
            offset=offset,
        )
        return [OrderOut(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self.queries.get_orders_count(self.conn)
        return row["total"]

    async def get_by_id(self, order_id: int) -> OrderOut | None:
        row = await self.queries.get_order_by_id(self.conn, id=order_id)
        return OrderOut(**row) if row else None

    async def get_by_number(self, order_number: str) -> OrderOut | None:
        row = await self.queries.get_order_by_number(
            self.conn,
            order_number=order_number,
        )
        return OrderOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_order(self.conn, **data)
        return result["id"]

    async def update(self, order_id: int, data: dict) -> bool:
        result = await self.queries.update_order(
            self.conn,
            id=order_id,
            **data,
        )
        return bool(result)

    async def delete(self, order_id: int) -> bool:
        result = await self.queries.delete_order(self.conn, id=order_id)
        return bool(result)


