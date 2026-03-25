from shop.app.core.exceptions import NotFoundError, OperationFailedError
from shop.app.repositories.protocols import ProductRepository
from shop.app.schemas.product_schemas import (
    ProductCreate,
    ProductOut,
    ProductResponse,
    ProductUpdate,
)
from shop.app.services.cache_service import CacheService
from shop.app.services.category_service import CategoryService


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        category_service: CategoryService,
        cache: CacheService,
        cache_ttl_seconds: int | None = None,
    ):
        self.product_repo = product_repo
        self.category_service = category_service
        self.cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_product(self, data: ProductCreate) -> dict:
        check_exist = await self.category_service.category_id_exists(data.category_id)
        if not check_exist:
            raise NotFoundError("Category")
        product_id = await self.product_repo.create(data.model_dump())

        if not product_id:
            raise OperationFailedError("Failed to create product")

        return {"id": product_id, "message": "Product created successfully"}

    async def get_product_by_id(self, product_id: int) -> ProductOut:
        product = await self.product_repo.get_by_id(product_id)

        if not product:
            raise NotFoundError("Product")

        return product

    async def get_all_products(self, limit: int, offset: int) -> list[ProductOut]:
        key = f"products:limit:{limit}:offset:{offset}"
        if await self.cache.exists(key):
            items_str = await self.cache.get_list(key)
            return [ProductOut.model_validate_json(s) for s in items_str]
        products = await self.product_repo.get_all(limit=limit, offset=offset)
        items_str = [p.model_dump_json() for p in products]
        await self.cache.set_list_atomic(key, items_str, ttl_seconds=self._cache_ttl_seconds)
        return products

    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductResponse:
        check_exist = await self._product_id_exists(product_id)
        if not check_exist:
            raise NotFoundError("Product")

        success = await self.product_repo.update(product_id, data.model_dump(exclude_unset=True))

        if not success:
            raise OperationFailedError("Failed to update product")

        return ProductResponse(id=product_id, message="Product updated successfully")

    async def delete_product(self, product_id: int) -> ProductResponse:
        check_exist = await self._product_id_exists(product_id)
        if not check_exist:
            raise NotFoundError("Product")

        success = await self.product_repo.delete(product_id)

        if not success:
            raise OperationFailedError("Failed to delete product")

        return ProductResponse(id=product_id, message="Product deleted successfully")

    async def _product_id_exists(self, product_id: int) -> bool:
        return await self.product_repo.exists_product_with_id(product_id)
