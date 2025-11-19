from shop.app.schemas.cart_schemas import CartOut


class CartRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self, limit: int, offset: int) -> list[CartOut]:
        rows = await self.queries.get_all_carts(
            self.conn,
            limit=limit,
            offset=offset,
        )
        return [CartOut(**row) for row in rows]

    async def get_by_id(self, cart_id: int) -> CartOut | None:
        row = await self.queries.get_cart_by_id(self.conn, id=cart_id)
        return CartOut(**row) if row else None

    async def get_by_user_id(self, user_id: int) -> CartOut | None:
        row = await self.queries.get_cart_by_user_id(
            self.conn,
            user_id=user_id,
        )
        return CartOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_cart(self.conn, **data)
        return result["id"]

    async def update(self, cart_id: int, data: dict) -> bool:
        result = await self.queries.update_cart(self.conn, id=cart_id, **data)
        return bool(result)

    async def delete(self, cart_id: int) -> bool:
        result = await self.queries.delete_cart(self.conn, id=cart_id)
        return bool(result)


