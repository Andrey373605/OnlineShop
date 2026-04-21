from fastapi import UploadFile

from shop.app.core.exceptions import (
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.models.domain.product_image import ProductImageCreateData
from shop.app.models.schemas import (
    ProductImageCreate,
    ProductImageOut,
    ProductImageResponse,
    ProductImagesDeleteResponse,
    ProductImageUpdate,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.s3_service import S3Service


class ProductImageService:
    def __init__(self, uow: UnitOfWork, s3_service: S3Service):
        self._uow = uow
        self._s3 = s3_service

    async def create_image(
        self, data: ProductImageCreate, file: UploadFile
    ) -> ProductImageResponse:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, data.product_id)
            image_name = await self._s3.upload_file(file)
            image_path = f"/media/{image_name}"
            db_data = ProductImageCreateData(
                product_id=data.product_id, image_path=image_path
            )
            image_id = await uow.product_images.create(db_data)
            if not image_id:
                raise OperationFailedError("Failed to create product image")
            await uow.commit()

        return ProductImageResponse(
            id=image_id,
            message="Product image created successfully",
        )

    async def get_image_by_id(self, image_id: int) -> ProductImageOut:
        async with self._uow as uow:
            return await self._get_image_or_raise(uow, image_id)

    async def get_images_by_product_id(self, product_id: int) -> list[ProductImageOut]:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, product_id)
            return await uow.product_images.get_by_product_id(product_id)

    async def update_image(
        self, image_id: int, data: ProductImageUpdate, file: UploadFile
    ) -> ProductImageResponse:
        async with self._uow as uow:
            existing_image = await self._get_image_or_raise(uow, image_id)

            payload = data.model_dump(exclude_unset=True)
            if not payload:
                raise DomainValidationError("No data provided to update product image")

            if "product_id" in payload:
                await self._ensure_product_exists(uow, payload["product_id"])

            success = await uow.product_images.update(image_id, payload)
            if not success:
                raise OperationFailedError("Failed to update product image")
            await uow.commit()

        return ProductImageResponse(
            id=existing_image.id,
            message="Product image updated successfully",
        )

    async def delete_image(self, image_id: int) -> ProductImageResponse:
        async with self._uow as uow:
            image = await self._get_image_or_raise(uow, image_id)

            success = await uow.product_images.delete(image_id)
            if not success:
                raise OperationFailedError("Failed to delete product image")
            await uow.commit()
        await self._s3.delete_file(image.image_path)

        return ProductImageResponse(
            id=image_id,
            message="Product image deleted successfully",
        )

    async def delete_images_by_product_id(
        self,
        product_id: int,
    ) -> ProductImagesDeleteResponse:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, product_id)
            images = await uow.product_images.get_by_product_id(product_id)
            deleted_ids = await uow.product_images.delete_by_product_id(product_id)
            await uow.commit()
        for image in images:
            await self._s3.delete_file(image.image_path)

        return ProductImagesDeleteResponse(
            product_id=product_id,
            deleted_ids=deleted_ids,
        )

    @staticmethod
    async def _get_image_or_raise(uow: UnitOfWork, image_id: int) -> ProductImageOut:
        image = await uow.product_images.get_by_id(image_id)
        if not image:
            raise NotFoundError("Product image")
        return image

    @staticmethod
    async def _ensure_product_exists(uow: UnitOfWork, product_id: int) -> None:
        exists = await uow.products.exists_product_with_id(product_id)
        if not exists:
            raise NotFoundError("Product")
