from shop.app.schemas.product_specification_schemas import ProductSpecificationOut


class ProductSpecificationRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self) -> list[ProductSpecificationOut]:
        rows = await self.queries.get_all_product_specifications(self.conn)
        return [ProductSpecificationOut(**row) for row in rows]

    async def get_by_id(self, specification_id: int) -> ProductSpecificationOut | None:
        row = await self.queries.get_product_specification_by_id(
            self.conn,
            id=specification_id,
        )
        return ProductSpecificationOut(**row) if row else None

    async def get_by_product_id(self, product_id: int) -> ProductSpecificationOut | None:
        row = await self.queries.get_product_specification_by_product_id(
            self.conn,
            product_id=product_id,
        )
        return ProductSpecificationOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_product_specification(
            self.conn,
            **data,
        )
        return result["id"]

    async def update(self, specification_id: int, data: dict) -> bool:
        result = await self.queries.update_product_specification(
            self.conn,
            id=specification_id,
            **data,
        )
        return bool(result)

    async def delete(self, specification_id: int) -> bool:
        result = await self.queries.delete_product_specification(
            self.conn,
            id=specification_id,
        )
        return bool(result)


