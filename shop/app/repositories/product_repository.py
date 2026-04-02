from shop.app.models.schemas import ProductOut


class ProductRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_id(self, product_id: int) -> ProductOut | None:
        """Возвращает продукт по id"""
        row = await self._queries.get_product_by_id(self._conn, id=product_id)
        return ProductOut(**row) if row else None

    async def get_all(self, limit: int, offset: int) -> list[ProductOut]:
        """Возвращает все продукты"""
        rows = await self._queries.get_all_products(
            self._conn, limit=limit, offset=offset
        )
        return [ProductOut(**row) for row in rows]

    async def get_total(self) -> int:
        """Возвращает общее количество товаров (для аналитики)."""
        row = await self._queries.get_products_count(self._conn)
        return row["total"]

    async def create(self, product_data: dict) -> int:
        """Возвращает ID созданного продукта"""
        result = await self._queries.create_product(self._conn, **product_data)
        return result["id"]

    async def update(self, product_id: int, update_data: dict) -> bool:
        """Возвращает успешность обновления"""
        result = await self._queries.update_product(
            self._conn, id=product_id, **update_data
        )
        return bool(result)

    async def delete(self, product_id: int) -> bool:
        """Возвращает успешность удаления"""
        result = await self._queries.delete_product(self._conn, id=product_id)
        return bool(result)

    async def exists_product_with_id(self, product_id: int) -> bool:
        """Проверяет существование категории по id"""
        result = await self._queries.check_product_id_exists(self._conn, id=product_id)
        return result["exists"]
