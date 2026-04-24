from shop.app.models.domain.product_image import ProductImageCreateData, ProductImage


class ProductImageRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_by_product_id(self, product_id: int) -> list[ProductImage]:
        rows = await self._queries.get_product_images_by_product_id(
            self._conn,
            product_id=product_id,
        )
        return [ProductImage(**row) for row in rows]

    async def get_by_id(self, image_id: int) -> ProductImage | None:
        row = await self._queries.get_product_image_by_id(self._conn, id=image_id)
        return ProductImage(**row) if row else None

    async def create(self, product: ProductImageCreateData) -> ProductImage:
        row = await self._queries.create_product_image(
            self._conn, product_id=product.product_id, storage_key=product.storage_key
        )
        return ProductImage(**row)

    async def update(self, image_id: int, data: dict) -> ProductImage:
        row = await self._queries.update_product_image(
            self._conn,
            id=image_id,
            **data,
        )
        return ProductImage(**row)

    async def delete(self, image_id: int) -> bool:
        result = await self._queries.delete_product_image(self._conn, id=image_id)
        return result

    async def delete_by_product_id(self, product_id: int) -> list[int]:
        rows = await self._queries.delete_product_images_by_product_id(
            self._conn,
            product_id=product_id,
        )
        return [row["id"] for row in rows]
