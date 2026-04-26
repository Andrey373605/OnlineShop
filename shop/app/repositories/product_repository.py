from shop.app.models.domain.product import Product


class ProductRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_id(self, product_id: int) -> Product | None:
        row = await self._queries.get_product_by_id(self._conn, id=product_id)
        return Product(**row) if row else None

    async def get_all(self, limit: int, offset: int) -> list[Product]:
        rows = await self._queries.get_all_products(self._conn, limit=limit, offset=offset)
        return [Product(**row) for row in rows]

    async def get_total(self) -> int:
        row = await self._queries.get_products_count(self._conn)
        return row["total"]

    async def create(self, product_data: dict) -> Product:
        row = await self._queries.create_product(self._conn, **product_data)
        return Product(**row)

    async def update(self, product_id: int, update_data: dict) -> Product:
        row = await self._queries.update_product(self._conn, id=product_id, **update_data)
        return Product(**row)

    async def delete(self, product_id: int) -> bool:
        row = await self._queries.delete_product(self._conn, id=product_id)
        return bool(row)

    async def exists_product_with_id(self, product_id: int) -> bool:
        row = await self._queries.check_product_id_exists(self._conn, id=product_id)
        return row["exists"]
