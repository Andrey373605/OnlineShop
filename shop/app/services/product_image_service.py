from fastapi import UploadFile

from shop.app.core.exceptions import (
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.core.ports.storage import StoragePort
from shop.app.models.domain.product_image import ProductImageCreateData
from shop.app.models.schemas import (
    ProductImageCreate,
    ProductImageOut,
    ProductImageResponse,
    ProductImagesDeleteResponse,
    ProductImageUpdate,
)
from shop.app.repositories.protocols import UnitOfWork


class ProductImageService:
    def __init__(
        self,
        uow: UnitOfWork,
        storage: StoragePort,
        media_url_prefix: str,
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._media_url_prefix = media_url_prefix.rstrip("/")

    async def create_image(
        self, data: ProductImageCreate, file: UploadFile, content_length: int | None = None
    ) -> ProductImageResponse:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, data.product_id)
            image_key = await self._storage.upload_file(file, content_length)
            image_path = self._build_media_url(image_key)
            db_data = ProductImageCreateData(product_id=data.product_id, image_path=image_path)
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
        await self._storage.delete_file(self._extract_storage_key(image.image_path))

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
            await self._storage.delete_file(self._extract_storage_key(image.image_path))

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

    def _build_media_url(self, storage_key: str) -> str:
        return f"{self._media_url_prefix}/{storage_key}"

    def _extract_storage_key(self, media_url: str) -> str:
        prefix = f"{self._media_url_prefix}/"
        if not media_url.startswith(prefix):
            raise DomainValidationError("Invalid media url")

        return media_url.removeprefix(prefix)
