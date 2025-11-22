
from shop.app.schemas.cart_item_schemas import CartItemOut


class CartItemRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_by_cart_id(self, cart_id: int) -> list[CartItemOut]:
        rows = await self.queries.get_cart_items_by_cart_id(
            self.conn,
            cart_id=cart_id,
        )
        return [CartItemOut(**row) for row in rows]

    async def get_by_id(self, item_id: int) -> CartItemOut | None:
        row = await self.queries.get_cart_item_by_id(self.conn, id=item_id)
        return CartItemOut(**row) if row else None

    async def get_by_cart_and_product(self, cart_id: int, product_id: int):
        row = await self.queries.get_cart_item_by_cart_and_product(
            self.conn,
            cart_id=cart_id,
            product_id=product_id,
        )
        return CartItemOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_cart_item(self.conn, **data)
        return result["id"]

    async def update(self, item_id: int, data: dict) -> bool:
        result = await self.queries.update_cart_item(
            self.conn,
            id=item_id,
            **data,
        )
        return bool(result)

    async def delete(self, item_id: int) -> bool:
        result = await self.queries.delete_cart_item(self.conn, id=item_id)
        return bool(result)

    async def delete_by_cart_id(self, cart_id: int):
        rows = await self.queries.delete_cart_items_by_cart_id(
            self.conn,
            cart_id=cart_id,
        )
        return [row["id"] for row in rows]


