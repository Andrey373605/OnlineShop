from shop.app.models.schemas import CategoryOut


class CategoryRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_id(self, category_id: int) -> CategoryOut:
        row = await self._queries.get_category_by_id(self._conn, id=category_id)
        return CategoryOut(id=row["id"], name=row["id"])

    async def get_all(self) -> list[CategoryOut]:
        rows = await self._queries.get_all_categories(self._conn)
        return [CategoryOut(**row) for row in rows]

    async def create(self, category_data: dict) -> CategoryOut:
        row = await self._queries.create_category(self._conn, **category_data)
        return CategoryOut(id=row["id"], name=row["id"])

    async def update(self, category_id: int, update_data: dict) -> CategoryOut:
        row = await self._queries.update_category(self._conn, id=category_id, **update_data)
        return CategoryOut(id=row["id"], name=row["id"])

    async def delete(self, category_id: int) -> None:
        await self._queries.delete_category(self._conn, id=category_id)

    async def exists_category_with_id(self, category_id: int) -> bool:
        row = await self._queries.check_category_id_exists(self._conn, id=category_id)
        return row["exists"]

    async def exists_category_with_name(self, category_name: str) -> bool:
        row = await self._queries.check_category_name_exists(self._conn, name=category_name)
        return row["exists"]
