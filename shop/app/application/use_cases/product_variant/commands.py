
from shop.app.application.dto.commands import CreateProductVariantCommand, UpdateProductVariantCommand, DeleteProductVariantCommand
from shop.app.application.dto.responses import ProductVariantResponse
from shop.app.application.use_cases.base import UseCase

class CreateProductVariantUseCase(UseCase):
    async def __call__(self, command: CreateProductVariantCommand) -> ProductVariantResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateProductVariantUseCase(UseCase):
    async def __call__(self, command: UpdateProductVariantCommand) -> ProductVariantResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteProductVariantUseCase(UseCase):
    async def __call__(self, command: DeleteProductVariantCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateProductVariantUseCase",
    "UpdateProductVariantUseCase",
    "DeleteProductVariantUseCase",
]
