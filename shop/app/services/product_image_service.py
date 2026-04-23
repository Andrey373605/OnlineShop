from shop.app.core.exceptions import (
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.core.ports.storage import StoragePort
from shop.app.models.domain.product_image import ProductImageCreateData
from shop.app.models.domain.upload_source import UploadSource
from shop.app.models.schemas import (
    ProductImageCreate,
    ProductImageOut,
    ProductImageResponse,
    ProductImagesDeleteResponse,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.media_url_builder import MediaUrlBuilder


class ProductImageService:
    def __init__(
        self, uow: UnitOfWork, storage: StoragePort, media_url_builder: MediaUrlBuilder
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._media_url_builder = media_url_builder

    async def create_image(
        self, data: ProductImageCreate, source: UploadSource
    ) -> ProductImageResponse:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, data.product_id)
            storage_key = await self._storage.upload(source)
            db_data = ProductImageCreateData(product_id=data.product_id, storage_key=storage_key)
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

    async def delete_image(self, image_id: int) -> ProductImageResponse:
        async with self._uow as uow:
            image = await self._get_image_or_raise(uow, image_id)

            success = await uow.product_images.delete(image_id)
            if not success:
                raise OperationFailedError("Failed to delete product image")
            await uow.commit()
        await self._storage.delete(image.storage_key)

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
            await self._storage.delete(image.storage_key)

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
