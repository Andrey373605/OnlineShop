from fastapi import HTTPException
from shop.app.repositories.product_repository import ProductRepository
from shop.app.schemas.product_schemas import ProductCreate, ProductUpdate, ProductOut, ProductResponse
from shop.app.services.category_service import CategoryService


class ProductService:
    def __init__(self, product_repo: ProductRepository, category_service: CategoryService):
        self.product_repo = product_repo
        self.category_service = category_service

    async def create_product(self, data: ProductCreate) -> dict:
        check_exist = await self.category_service.category_id_exists(data.category_id)
        if not check_exist:
            raise HTTPException(status_code=400, detail="Category not found")
        product_id = await self.product_repo.create(data.model_dump())

        if not product_id:
            raise HTTPException(status_code=500, detail="Failed to create product")

        return {"id": product_id, "message": "Product created successfully"}

    async def get_product_by_id(self, product_id: int) -> ProductOut:
        product = await self.product_repo.get_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

    async def get_all_products(self, limit: int, offset: int) -> list[ProductOut]:
        products = await self.product_repo.get_all(limit=limit, offset=offset)
        return products

    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductResponse:
        check_exist = await self._product_id_exists(product_id)
        if not check_exist:
            raise HTTPException(status_code=404, detail="Product not found")

        success = await self.product_repo.update(product_id, data.model_dump(exclude_unset=True))

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update product")

        return ProductResponse(id=product_id, message="Product updated successfully")

    async def delete_product(self, product_id: int) -> ProductResponse:
        check_exist = await self._product_id_exists(product_id)
        if not check_exist:
            raise HTTPException(status_code=404, detail="Product not found")

        # Бизнес-логика: можно ли удалять?
        # if product.has_products():
        #     raise HTTPException(status_code=400, detail="Cannot delete product with products")

        success = await self.product_repo.delete(product_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete product")

        return ProductResponse(id=product_id, message="Product deleted successfully")

    async def _product_id_exists(self, product_id: int) -> bool:
        return await self.product_repo.exists_product_with_id(product_id)


