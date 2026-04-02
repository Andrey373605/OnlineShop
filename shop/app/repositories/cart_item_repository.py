from shop.app.models.schemas import CartItemOut


class CartItemRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_cart_id(self, cart_id: int) -> list[CartItemOut]:
        rows = await self._queries.get_cart_items_by_cart_id(
            self._conn,
            cart_id=cart_id,
        )
        return [CartItemOut(**row) for row in rows]

    async def get_by_id(self, item_id: int) -> CartItemOut | None:
        row = await self._queries.get_cart_item_by_id(self._conn, id=item_id)
        return CartItemOut(**row) if row else None

    async def get_by_cart_and_product(self, cart_id: int, product_id: int):
        row = await self._queries.get_cart_item_by_cart_and_product(
            self._conn,
            cart_id=cart_id,
            product_id=product_id,
        )
        return CartItemOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._queries.create_cart_item(self._conn, **data)
        return result["id"]

    async def update(self, item_id: int, data: dict) -> bool:
        result = await self._queries.update_cart_item(
            self._conn,
            id=item_id,
            **data,
        )
        return bool(result)

    async def delete(self, item_id: int) -> bool:
        result = await self._queries.delete_cart_item(self._conn, id=item_id)
        return bool(result)

    async def delete_by_cart_id(self, cart_id: int):
        rows = await self._queries.delete_cart_items_by_cart_id(
            self._conn,
            cart_id=cart_id,
        )
        return [row["id"] for row in rows]
