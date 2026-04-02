from shop.app.models.schemas import OrderItemOut


class OrderItemRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_order_id(self, order_id: int) -> list[OrderItemOut]:
        rows = await self._queries.get_order_items_by_order_id(
            self._conn,
            order_id=order_id,
        )
        return [OrderItemOut(**row) for row in rows]

    async def get_by_id(self, item_id: int) -> OrderItemOut | None:
        row = await self._queries.get_order_item_by_id(self._conn, id=item_id)
        return OrderItemOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._queries.create_order_item(self._conn, **data)
        return result["id"]

    async def update(self, item_id: int, data: dict) -> bool:
        result = await self._queries.update_order_item(
            self._conn,
            id=item_id,
            **data,
        )
        return bool(result)

    async def delete(self, item_id: int) -> bool:
        result = await self._queries.delete_order_item(self._conn, id=item_id)
        return bool(result)

    async def delete_by_order_id(self, order_id: int):
        rows = await self._queries.delete_order_items_by_order_id(
            self._conn,
            order_id=order_id,
        )
        return [row["id"] for row in rows]
