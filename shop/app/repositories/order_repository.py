from shop.app.models.schemas import OrderOut


class OrderRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_all(self, limit: int, offset: int) -> list[OrderOut]:
        rows = await self._queries.get_all_orders(
            self._conn,
            limit=limit,
            offset=offset,
        )
        return [OrderOut(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self._queries.get_orders_count(self._conn)
        return row["total"]

    async def get_by_id(self, order_id: int) -> OrderOut | None:
        row = await self._queries.get_order_by_id(self._conn, id=order_id)
        return OrderOut(**row) if row else None

    async def get_by_number(self, order_number: str) -> OrderOut | None:
        row = await self._queries.get_order_by_number(
            self._conn,
            order_number=order_number,
        )
        return OrderOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._queries.create_order(self._conn, **data)
        return result["id"]

    async def update(self, order_id: int, data: dict) -> bool:
        result = await self._queries.update_order(
            self._conn,
            id=order_id,
            **data,
        )
        return bool(result)

    async def delete(self, order_id: int) -> bool:
        result = await self._queries.delete_order(self._conn, id=order_id)
        return bool(result)
