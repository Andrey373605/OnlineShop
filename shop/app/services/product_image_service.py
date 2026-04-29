import logging

from shop.app.core.exceptions import (
    EntityNotFoundError,
    ApplicationUnavailableError,
    DomainValidationError,
    ConflictError,
    StorageValidationError,
    StorageUnavailableError,
)
from shop.app.core.ports.file_storage import FileStoragePort
from shop.app.models.domain.product_image import (
    ProductImageCreateData,
    ProductImage,
    ProductImagesDeleteResult,
)
from shop.app.models.domain.upload_source import UploadSource
from shop.app.models.schemas import (
    ProductImageCreate,
)
from shop.app.repositories.exceptions import (
    RepositoryRecordNotFoundError,
    RepositoryUnavailableError,
    RepositoryMappingError,
    RepositoryUnexpectedResultError,
    RepositoryForeignKeyError,
    RepositoryUniqueConstraintError,
)
from shop.app.repositories.protocols import UnitOfWork


logger = logging.getLogger(__name__)


class ProductImageService:
    def __init__(self, uow: UnitOfWork, storage: FileStoragePort) -> None:
        self._uow = uow
        self._storage = storage

    async def create_image(self, data: ProductImageCreate, source: UploadSource) -> ProductImage:
        try:
            storage_key = await self._storage.upload(source)
        except StorageValidationError as exc:
            raise DomainValidationError("Invalid image file") from exc
        except StorageUnavailableError as exc:
            raise ApplicationUnavailableError("Image storage is unavailable") from exc

        try:
            async with self._uow as uow:
                product_image_data = ProductImageCreateData.from_input(
                    data=data, storage_key=storage_key
                )
                product_image = await uow.product_images.create(product_image_data)
                await uow.commit()
                return product_image
        except RepositoryForeignKeyError as exc:
            await self._delete_orphan_object(storage_key)
            raise EntityNotFoundError(
                "Product not found",
                details={"product_id": data.product_id},
            ) from exc
        except RepositoryUniqueConstraintError as exc:
            await self._delete_orphan_object(storage_key)
            raise ConflictError(
                "Product image already exists",
                details={"product_id": data.product_id},
            ) from exc
        except (
            RepositoryUnavailableError,
            RepositoryMappingError,
            RepositoryUnexpectedResultError,
        ) as exc:
            await self._delete_orphan_object(storage_key)
            raise ApplicationUnavailableError("Failed to create product image") from exc

    async def get_image_by_id(self, image_id: int) -> ProductImage:
        async with self._uow as uow:
            try:
                return await uow.product_images.get_by_id(image_id)
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Product image not found",
                    details={"image_id": image_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to fetch product image") from exc

    async def get_images_by_product_id(self, product_id: int) -> list[ProductImage]:
        async with self._uow as uow:
            try:
                return await uow.product_images.get_by_product_id(product_id)
            except RepositoryUnavailableError as exc:
                raise ApplicationUnavailableError("Failed to fetch product images") from exc
            except RepositoryMappingError as exc:
                raise ApplicationUnavailableError("Failed to map product images") from exc

    async def delete_image(self, image_id: int) -> None:
        async with self._uow as uow:
            try:
                image = await uow.product_images.delete(image_id)
                await uow.commit()
            except RepositoryRecordNotFoundError as exc:
                raise EntityNotFoundError(
                    "Product image not found",
                    details={"image_id": image_id},
                ) from exc
            except RepositoryForeignKeyError as exc:
                raise ConflictError(
                    "Product image is referenced by another entity",
                    details={"image_id": image_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError("Failed to delete product image") from exc

        await self._delete_storage_object_best_effort(image.storage_key)

    async def delete_images_by_product_id(
        self,
        product_id: int,
    ) -> ProductImagesDeleteResult:
        async with self._uow as uow:
            exists = await uow.products.exists_product_with_id(product_id)
            if not exists:
                raise EntityNotFoundError(
                    "Product not found",
                    details={"product_id": product_id},
                )

            try:
                images = await uow.product_images.get_by_product_id(product_id)
                deleted_ids = await uow.product_images.delete_by_product_id(product_id)
                await uow.commit()
            except RepositoryForeignKeyError as exc:
                raise ConflictError(
                    "Product image is referenced by another entity",
                    details={"product_id": product_id},
                ) from exc
            except (
                RepositoryUnavailableError,
                RepositoryMappingError,
                RepositoryUnexpectedResultError,
            ) as exc:
                raise ApplicationUnavailableError(
                    "Failed to delete product images",
                    details={"product_id": product_id},
                ) from exc

        for image in images:
            await self._delete_storage_object_best_effort(image.storage_key)

        return ProductImagesDeleteResult(
            product_id=product_id,
            deleted_ids=deleted_ids,
        )

    async def _delete_orphan_object(self, storage_key: str) -> None:
        try:
            await self._storage.delete(storage_key)
        except Exception:
            logger.warning(
                "Failed to delete orphan product image: %s",
                storage_key,
                exc_info=True,
            )

    async def _delete_storage_object_best_effort(self, storage_key: str) -> None:
        try:
            await self._storage.delete(storage_key)
        except Exception:
            logger.warning(
                "Failed to delete product image object: %s",
                storage_key,
                exc_info=True,
            )
