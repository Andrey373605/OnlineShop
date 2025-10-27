from shop.app.schemas.product_schemas import ProductOut


class ProductRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_by_id(self, product_id: int) -> ProductOut | None:
        """Возвращает продукт по id"""
        row = await self.queries.get_product_by_id(
            self.conn,
            id=product_id
        )
        return ProductOut(**row) if row else None

    async def get_all(self, limit: int, offset: int) -> list[ProductOut]:
        """Возвращает все продукты"""
        rows = await self.queries.get_all_products(self.conn, limit=limit, offset=offset)
        return [ProductOut(**row) for row in rows]

    async def create(self, product_data: dict) -> int:
        """Возвращает ID созданного продукта"""
        result = await self.queries.create_product(
            self.conn,
            **product_data
        )
        return result['id']

    async def update(self, product_id: int, update_data: dict) -> bool:
        """Возвращает успешность обновления"""
        result = await self.queries.update_product(
            self.conn,
            id=product_id,
            **update_data
        )
        return bool(result)

    async def delete(self, product_id: int) -> bool:
        """Возвращает успешность удаления"""
        result = await self.queries.delete_product(
            self.conn,
            id=product_id
        )
        return bool(result)

    async def exists_product_with_id(self, product_id: int) -> bool:
        """Проверяет существование категории по id"""
        result = await self.queries.check_product_id_exists(
            self.conn,
            id=product_id
        )
        return result['exists']
