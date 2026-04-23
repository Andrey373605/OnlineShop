from shop.app.models.domain.product_image import ProductImageCreateData
from shop.app.models.schemas import ProductImageOut


class ProductImageRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_product_id(self, product_id: int) -> list[ProductImageOut]:
        rows = await self._queries.get_product_images_by_product_id(
            self._conn,
            product_id=product_id,
        )
        return [ProductImageOut(**row) for row in rows]

    async def get_by_id(self, image_id: int) -> ProductImageOut | None:
        row = await self._queries.get_product_image_by_id(self._conn, id=image_id)
        return ProductImageOut(**row) if row else None

    async def create(self, product: ProductImageCreateData) -> int:
        result = await self._queries.create_product_image(
            self._conn, product_id=product.product_id, storage_key=product.storage_key
        )
        return result["id"]

    async def update(self, image_id: int, data: dict) -> bool:
        result = await self._queries.update_product_image(
            self._conn,
            id=image_id,
            **data,
        )
        return bool(result)

    async def delete(self, image_id: int) -> bool:
        result = await self._queries.delete_product_image(self._conn, id=image_id)
        return bool(result)

    async def delete_by_product_id(self, product_id: int):
        rows = await self._queries.delete_product_images_by_product_id(
            self._conn,
            product_id=product_id,
        )
        return [row["id"] for row in rows]
