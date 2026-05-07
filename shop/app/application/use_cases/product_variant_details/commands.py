
from shop.app.application.dto.commands import CreateProductVariantDetailsCommand, UpdateProductVariantDetailsCommand, DeleteProductVariantDetailsCommand
from shop.app.application.dto.responses import ProductVariantDetailsResponse
from shop.app.application.use_cases.base import UseCase

class CreateProductVariantDetailsUseCase(UseCase):
    async def __call__(self, command: CreateProductVariantDetailsCommand) -> ProductVariantDetailsResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateProductVariantDetailsUseCase(UseCase):
    async def __call__(self, command: UpdateProductVariantDetailsCommand) -> ProductVariantDetailsResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteProductVariantDetailsUseCase(UseCase):
    async def __call__(self, command: DeleteProductVariantDetailsCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateProductVariantDetailsUseCase",
    "UpdateProductVariantDetailsUseCase",
    "DeleteProductVariantDetailsUseCase",
]
