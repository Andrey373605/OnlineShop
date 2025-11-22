from fastapi import HTTPException

from shop.app.repositories.product_image_repository import ProductImageRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.schemas.product_image_schemas import (
    ProductImageCreate,
    ProductImageOut,
    ProductImageResponse,
    ProductImageUpdate,
    ProductImagesDeleteResponse,
)


class ProductImageService:
    def __init__(
        self,
        image_repo: ProductImageRepository,
        product_repo: ProductRepository,
    ):
        self.image_repo = image_repo
        self.product_repo = product_repo

    async def create_image(self, data: ProductImageCreate) -> ProductImageResponse:
        await self._ensure_product_exists(data.product_id)

        image_id = await self.image_repo.create(data.model_dump())
        if not image_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to create product image",
            )

        return ProductImageResponse(
            id=image_id,
            message="Product image created successfully",
        )

    async def get_image_by_id(self, image_id: int) -> ProductImageOut:
        return await self._get_image_or_404(image_id)

    async def get_images_by_product_id(self, product_id: int) -> list[ProductImageOut]:
        await self._ensure_product_exists(product_id)
        return await self.image_repo.get_by_product_id(product_id)

    async def update_image(
        self,
        image_id: int,
        data: ProductImageUpdate,
    ) -> ProductImageResponse:
        existing_image = await self._get_image_or_404(image_id)

        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise HTTPException(
                status_code=400,
                detail="No data provided to update product image",
            )

        if "product_id" in payload:
            await self._ensure_product_exists(payload["product_id"])

        success = await self.image_repo.update(image_id, payload)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update product image",
            )

        return ProductImageResponse(
            id=existing_image.id,
            message="Product image updated successfully",
        )

    async def delete_image(self, image_id: int) -> ProductImageResponse:
        await self._get_image_or_404(image_id)

        success = await self.image_repo.delete(image_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete product image",
            )

        return ProductImageResponse(
            id=image_id,
            message="Product image deleted successfully",
        )

    async def delete_images_by_product_id(
        self,
        product_id: int,
    ) -> ProductImagesDeleteResponse:
        await self._ensure_product_exists(product_id)
        deleted_ids = await self.image_repo.delete_by_product_id(product_id)

        return ProductImagesDeleteResponse(
            product_id=product_id,
            deleted_ids=deleted_ids,
        )

    async def _get_image_or_404(self, image_id: int) -> ProductImageOut:
        image = await self.image_repo.get_by_id(image_id)
        if not image:
            raise HTTPException(
                status_code=404,
                detail="Product image not found",
            )
        return image

    async def _ensure_product_exists(self, product_id: int) -> None:
        exists = await self.product_repo.exists_product_with_id(product_id)
        if not exists:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )



