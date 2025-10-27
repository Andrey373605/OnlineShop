from shop.app.schemas.category_schemas import CategoryOut


class CategoryRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_by_id(self, category_id: int) -> CategoryOut | None:
        """Возвращает категорию по id"""
        row = await self.queries.get_category_by_id(
            self.conn,
            id=category_id
        )
        return CategoryOut(**row) if row else None

    async def get_all(self) -> list[CategoryOut]:
        """Возвращает все категории"""
        rows = await self.queries.get_all_categories(self.conn)
        return [CategoryOut(**row) for row in rows]

    async def create(self, category_data: dict) -> int:
        """Возвращает ID созданной категории"""
        result = await self.queries.create_category(
            self.conn,
            **category_data
        )
        return result['id']

    async def update(self, category_id: int, update_data: dict) -> bool:
        """Возвращает успешность обновления"""
        result = await self.queries.update_category(
            self.conn,
            id=category_id,
            **update_data
        )
        return bool(result)

    async def delete(self, category_id: int) -> bool:
        """Возвращает успешность удаления"""
        result = await self.queries.delete_category(
            self.conn,
            id=category_id
        )
        return bool(result)

    async def exists_category_with_id(self, category_id: int) -> bool:
        """Проверяет существование категории по id"""
        result = await self.queries.check_category_id_exists(
            self.conn, 
            id=category_id
        )
        return result['exists']

    async def exists_category_with_name(self, category_name: str) -> bool:
        """Проверяет существование категории по name"""
        result = await self.queries.check_category_name_exists(
            self.conn,
            name=category_name
        )
        return result['exists']