from shop.app.models.schemas import CartItemOut
from shop.app.repositories.protocols import CartItemRepository


class CartItemRepositorySql(CartItemRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_by_cart_id(self, cart_id: int) -> list[CartItemOut]:
        rows = await self._conn.fetch(
            """
            SELECT ci.id, ci.cart_id, ci.product_id, p.title AS product_title, p.price AS product_price,
                   ci.quantity, (p.price * ci.quantity) AS line_total
            FROM cart_items ci
            LEFT JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = $1
            ORDER BY ci.id;
            """,
            cart_id,
        )
        return [CartItemOut(**row) for row in rows]

    async def get_by_id(self, item_id: int) -> CartItemOut | None:
        row = await self._conn.fetchrow(
            "SELECT id, cart_id, product_id, quantity FROM cart_items WHERE id = $1;",
            item_id,
        )
        return CartItemOut(**row) if row else None

    async def get_by_cart_and_product(self, cart_id: int, product_id: int):
        row = await self._conn.fetchrow(
            """
            SELECT id, cart_id, product_id, quantity
            FROM cart_items
            WHERE cart_id = $1 AND product_id = $2;
            """,
            cart_id,
            product_id,
        )
        return CartItemOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO cart_items (cart_id, product_id, quantity)
            VALUES ($1, $2, $3)
            RETURNING id;
            """,
            data.get("cart_id"),
            data.get("product_id"),
            data.get("quantity"),
        )
        return result["id"]

    async def update(self, item_id: int, data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE cart_items
            SET cart_id = COALESCE($2, cart_id),
                product_id = COALESCE($3, product_id),
                quantity = COALESCE($4, quantity)
            WHERE id = $1
            RETURNING id, cart_id, product_id, quantity;
            """,
            item_id,
            data.get("cart_id"),
            data.get("product_id"),
            data.get("quantity"),
        )
        return bool(result)

    async def delete(self, item_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM cart_items WHERE id = $1 RETURNING id;",
            item_id,
        )
        return bool(result)

    async def delete_by_cart_id(self, cart_id: int):
        rows = await self._conn.fetch(
            "DELETE FROM cart_items WHERE cart_id = $1 RETURNING id;",
            cart_id,
        )
        return [row["id"] for row in rows]
