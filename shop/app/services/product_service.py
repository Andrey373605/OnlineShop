from shop.app.core.exceptions import NotFoundError, OperationFailedError
from shop.app.repositories.protocols import UnitOfWork
from shop.app.schemas.product_schemas import (
    ProductCreate,
    ProductOut,
    ProductResponse,
    ProductUpdate,
)
from shop.app.services.cache_service import CacheService


class ProductService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        cache_ttl_seconds: int | None = None,
    ):
        self.uow = uow
        self.cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds
        self._cache_pattern = "products:limit:*"

    async def create_product(self, data: ProductCreate) -> dict:
        async with self.uow as uow:
            if not await uow.categories.exists_category_with_id(data.category_id):
                raise NotFoundError("Category")

            product_id = await uow.products.create(data.model_dump())
            if not product_id:
                raise OperationFailedError("Failed to create product")
            await uow.commit()

        await self.cache.delete_by_pattern(self._cache_pattern)
        return {"id": product_id, "message": "Product created successfully"}

    async def get_product_by_id(self, product_id: int) -> ProductOut:
        async with self.uow as uow:
            product = await uow.products.get_by_id(product_id)
            if not product:
                raise NotFoundError("Product")
            return product

    async def get_all_products(self, limit: int, offset: int) -> list[ProductOut]:
        key = f"products:limit:{limit}:offset:{offset}"
        if await self.cache.exists(key):
            items_str = await self.cache.get_list(key)
            return [ProductOut.model_validate_json(s) for s in items_str]

        async with self.uow as uow:
            products = await uow.products.get_all(limit=limit, offset=offset)

        items_str = [p.model_dump_json() for p in products]
        await self.cache.set_list_atomic(key, items_str, ttl_seconds=self._cache_ttl_seconds)
        return products

    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductResponse:
        async with self.uow as uow:
            if not await uow.products.exists_product_with_id(product_id):
                raise NotFoundError("Product")

            success = await uow.products.update(product_id, data.model_dump(exclude_unset=True))
            if not success:
                raise OperationFailedError("Failed to update product")
            await uow.commit()

        await self.cache.delete_by_pattern(self._cache_pattern)
        return ProductResponse(id=product_id, message="Product updated successfully")

    async def delete_product(self, product_id: int) -> ProductResponse:
        async with self.uow as uow:
            if not await uow.products.exists_product_with_id(product_id):
                raise NotFoundError("Product")

            success = await uow.products.delete(product_id)
            if not success:
                raise OperationFailedError("Failed to delete product")
            await uow.commit()

        await self.cache.delete_by_pattern(self._cache_pattern)
        return ProductResponse(id=product_id, message="Product deleted successfully")
