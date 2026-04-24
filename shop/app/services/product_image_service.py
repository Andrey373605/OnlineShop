from shop.app.core.exceptions import (
    NotFoundError,
    OperationFailedError,
)
from shop.app.core.ports.storage import StoragePort
from shop.app.models.domain.product_image import (
    ProductImageCreateData,
    ProductImage,
    ProductImagesDeleteResult,
)
from shop.app.models.domain.upload_source import UploadSource
from shop.app.models.schemas import (
    ProductImageCreate,
)
from shop.app.repositories.protocols import UnitOfWork


class ProductImageService:
    def __init__(self, uow: UnitOfWork, storage: StoragePort) -> None:
        self._uow = uow
        self._storage = storage

    async def create_image(self, data: ProductImageCreate, source: UploadSource) -> ProductImage:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, data.product_id)
            storage_key = await self._storage.upload(source)
            product_image_data = ProductImageCreateData(
                product_id=data.product_id, storage_key=storage_key
            )
            product_image = await uow.product_images.create(product_image_data)
            if not product_image:
                raise OperationFailedError("Failed to create product image")
            await uow.commit()

        return product_image

    async def get_image_by_id(self, image_id: int) -> ProductImage:
        async with self._uow as uow:
            return await self._get_image_or_raise(uow, image_id)

    async def get_images_by_product_id(self, product_id: int) -> list[ProductImage]:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, product_id)
            return await uow.product_images.get_by_product_id(product_id)

    async def delete_image(self, image_id: int) -> None:
        async with self._uow as uow:
            image = await self._get_image_or_raise(uow, image_id)

            success = await uow.product_images.delete(image_id)
            if not success:
                raise OperationFailedError("Failed to delete product image")
            await uow.commit()
        await self._storage.delete(image.storage_key)

    async def delete_images_by_product_id(
        self,
        product_id: int,
    ) -> ProductImagesDeleteResult:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, product_id)
            images = await uow.product_images.get_by_product_id(product_id)
            deleted_ids = await uow.product_images.delete_by_product_id(product_id)
            await uow.commit()

        for image in images:
            await self._storage.delete(image.storage_key)

        return ProductImagesDeleteResult(
            product_id=product_id,
            deleted_ids=deleted_ids,
        )

    @staticmethod
    async def _get_image_or_raise(uow: UnitOfWork, image_id: int) -> ProductImage:
        image = await uow.product_images.get_by_id(image_id)
        if not image:
            raise NotFoundError("Product image")
        return image

    @staticmethod
    async def _ensure_product_exists(uow: UnitOfWork, product_id: int) -> None:
        exists = await uow.products.exists_product_with_id(product_id)
        if not exists:
            raise NotFoundError("Product")
