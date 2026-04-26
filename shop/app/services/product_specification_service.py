from shop.app.core.exceptions import (
    DomainValidationError,
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
    ) -> ProductSpecificationOut:
        async with self._uow as uow:
            specification_id = await uow.product_specifications.create(data.model_dump())
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
            return await uow.product_specifications.get_by_id(specification_id)

    async def get_specification_by_product_id(
        self,
        product_id: int,
    ) -> ProductSpecificationOut:
        async with self._uow as uow:
            specification = await uow.product_specifications.get_by_product_id(product_id)
            return specification

    async def update_specification(
        self,
        specification_id: int,
        data: ProductSpecificationUpdate,
    ) -> ProductSpecificationOut:
        async with self._uow as uow:
            await uow.product_specifications.get_by_id(specification_id)

            payload = data.model_dump(exclude_unset=True)
            if not payload:
                raise DomainValidationError("No data provided to update product specification")

            specification = await uow.product_specifications.update(specification_id, payload)

            await uow.commit()

        return specification

    async def delete_specification(
        self,
        specification_id: int,
    ) -> None:
        async with self._uow as uow:
            await uow.product_specifications.get_by_id(specification_id)

            await uow.product_specifications.delete(specification_id)
            await uow.commit()

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification deleted successfully",
        )
