from shop.app.schemas.cart_schemas import CartOut


class CartRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_all(self, limit: int, offset: int) -> list[CartOut]:
        rows = await self._queries.get_all_carts(
            self._conn,
            limit=limit,
            offset=offset,
        )
        return [CartOut(**row) for row in rows]

    async def get_by_id(self, cart_id: int) -> CartOut | None:
        row = await self._queries.get_cart_by_id(self._conn, id=cart_id)
        return CartOut(**row) if row else None

    async def get_by_user_id(self, user_id: int) -> CartOut | None:
        row = await self._queries.get_cart_by_user_id(
            self._conn,
            user_id=user_id,
        )
        return CartOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._queries.create_cart(self._conn, **data)
        return result["id"]

    async def update(self, cart_id: int, data: dict) -> bool:
        result = await self._queries.update_cart(self._conn, id=cart_id, **data)
        return bool(result)

    async def delete(self, cart_id: int) -> bool:
        result = await self._queries.delete_cart(self._conn, id=cart_id)
        return bool(result)


