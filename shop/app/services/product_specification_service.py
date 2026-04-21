from shop.app.core.exceptions import (
    AlreadyExistsError,
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.models.schemas import (
    ProductSpecificationCreate,
    ProductSpecificationOut,
    ProductSpecificationResponse,
    ProductSpecificationUpdate,
)
from shop.app.repositories.protocols import UnitOfWork


class ProductSpecificationService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def create_specification(
        self,
        data: ProductSpecificationCreate,
    ) -> ProductSpecificationResponse:
        async with self._uow as uow:
            await self._ensure_product_exists(uow, data.product_id)

            existing = await uow.product_specifications.get_by_product_id(
                data.product_id
            )
            if existing:
                raise AlreadyExistsError(
                    "Product specification",
                    "Product specification already exists for this product",
                )

            specification_id = await uow.product_specifications.create(
                data.model_dump()
            )
            if not specification_id:
                raise OperationFailedError("Failed to create product specification")
            await uow.commit()

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification created successfully",
        )

    async def get_all_specifications(self) -> list[ProductSpecificationOut]:
        async with self._uow as uow:
            return await uow.product_specifications.get_all()

    async def get_specification_by_id(
        self,
        specification_id: int,
    ) -> ProductSpecificationOut:
        async with self._uow as uow:
            return await self._get_specification_or_raise(uow, specification_id)

    async def get_specification_by_product_id(
        self,
        product_id: int,
    ) -> ProductSpecificationOut:
        async with self._uow as uow:
            specification = await uow.product_specifications.get_by_product_id(
                product_id
            )
            if not specification:
                raise NotFoundError("Product specification")
            return specification

    async def update_specification(
        self,
        specification_id: int,
        data: ProductSpecificationUpdate,
    ) -> ProductSpecificationResponse:
        async with self._uow as uow:
            await self._get_specification_or_raise(uow, specification_id)

            payload = data.model_dump(exclude_unset=True)
            if not payload:
                raise DomainValidationError(
                    "No data provided to update product specification"
                )

            if "product_id" in payload:
                await self._ensure_product_exists(uow, payload["product_id"])

            success = await uow.product_specifications.update(specification_id, payload)
            if not success:
                raise OperationFailedError("Failed to update product specification")
            await uow.commit()

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification updated successfully",
        )

    async def delete_specification(
        self,
        specification_id: int,
    ) -> ProductSpecificationResponse:
        async with self._uow as uow:
            await self._get_specification_or_raise(uow, specification_id)

            success = await uow.product_specifications.delete(specification_id)
            if not success:
                raise OperationFailedError("Failed to delete product specification")
            await uow.commit()

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification deleted successfully",
        )

    @staticmethod
    async def _get_specification_or_raise(
        uow: UnitOfWork,
        specification_id: int,
    ) -> ProductSpecificationOut:
        specification = await uow.product_specifications.get_by_id(specification_id)
        if not specification:
            raise NotFoundError("Product specification")
        return specification

    @staticmethod
    async def _ensure_product_exists(uow: UnitOfWork, product_id: int) -> None:
        exists = await uow.products.exists_product_with_id(product_id)
        if not exists:
            raise NotFoundError("Product")
