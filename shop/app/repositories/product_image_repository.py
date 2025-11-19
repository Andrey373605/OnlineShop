from shop.app.schemas.product_image_schemas import ProductImageOut


class ProductImageRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_by_product_id(self, product_id: int) -> list[ProductImageOut]:
        rows = await self.queries.get_product_images_by_product_id(
            self.conn,
            product_id=product_id,
        )
        return [ProductImageOut(**row) for row in rows]

    async def get_by_id(self, image_id: int) -> ProductImageOut | None:
        row = await self.queries.get_product_image_by_id(self.conn, id=image_id)
        return ProductImageOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_product_image(self.conn, **data)
        return result["id"]

    async def update(self, image_id: int, data: dict) -> bool:
        result = await self.queries.update_product_image(
            self.conn,
            id=image_id,
            **data,
        )
        return bool(result)

    async def delete(self, image_id: int) -> bool:
        result = await self.queries.delete_product_image(self.conn, id=image_id)
        return bool(result)

    async def delete_by_product_id(self, product_id: int):
        rows = await self.queries.delete_product_images_by_product_id(
            self.conn,
            product_id=product_id,
        )
        return [row["id"] for row in rows]


