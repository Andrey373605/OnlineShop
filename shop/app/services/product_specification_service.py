from shop.app.core.exceptions import (
    AlreadyExistsError,
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.repositories.protocols import (
    ProductRepository,
    ProductSpecificationRepository,
)
from shop.app.schemas.product_specification_schemas import (
    ProductSpecificationCreate,
    ProductSpecificationOut,
    ProductSpecificationResponse,
    ProductSpecificationUpdate,
)


class ProductSpecificationService:
    def __init__(
            self,
            specification_repo: ProductSpecificationRepository,
            product_repo: ProductRepository,
    ):
        self.specification_repo = specification_repo
        self.product_repo = product_repo

    async def create_specification(
            self,
            data: ProductSpecificationCreate,
    ) -> ProductSpecificationResponse:
        await self._ensure_product_exists(data.product_id)

        existing = await self.specification_repo.get_by_product_id(data.product_id)
        if existing:
            raise AlreadyExistsError(
                "Product specification",
                "Product specification already exists for this product",
            )

        specification_id = await self.specification_repo.create(data.model_dump())
        if not specification_id:
            raise OperationFailedError("Failed to create product specification")

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification created successfully",
        )

    async def get_all_specifications(self) -> list[ProductSpecificationOut]:
        return await self.specification_repo.get_all()

    async def get_specification_by_id(
            self,
            specification_id: int,
    ) -> ProductSpecificationOut:
        return await self._get_specification_or_raise(specification_id)

    async def get_specification_by_product_id(
            self,
            product_id: int,
    ) -> ProductSpecificationOut:
        specification = await self.specification_repo.get_by_product_id(product_id)
        if not specification:
            raise NotFoundError("Product specification")
        return specification

    async def update_specification(
            self,
            specification_id: int,
            data: ProductSpecificationUpdate,
    ) -> ProductSpecificationResponse:
        await self._get_specification_or_raise(specification_id)

        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise DomainValidationError("No data provided to update product specification")

        if "product_id" in payload:
            await self._ensure_product_exists(payload["product_id"])

        success = await self.specification_repo.update(specification_id, payload)
        if not success:
            raise OperationFailedError("Failed to update product specification")

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification updated successfully",
        )

    async def delete_specification(
            self,
            specification_id: int,
    ) -> ProductSpecificationResponse:
        await self._get_specification_or_raise(specification_id)

        success = await self.specification_repo.delete(specification_id)
        if not success:
            raise OperationFailedError("Failed to delete product specification")

        return ProductSpecificationResponse(
            id=specification_id,
            message="Product specification deleted successfully",
        )

    async def _get_specification_or_raise(
            self,
            specification_id: int,
    ) -> ProductSpecificationOut:
        specification = await self.specification_repo.get_by_id(specification_id)
        if not specification:
            raise NotFoundError("Product specification")
        return specification

    async def _ensure_product_exists(self, product_id: int) -> None:
        exists = await self.product_repo.exists_product_with_id(product_id)
        if not exists:
            raise NotFoundError("Product")
