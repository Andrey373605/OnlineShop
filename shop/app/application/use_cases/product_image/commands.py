
from shop.app.application.dto.commands import CreateProductImageCommand, UpdateProductImageCommand, DeleteProductImageCommand
from shop.app.application.dto.responses import ProductImageResponse
from shop.app.application.use_cases.base import UseCase

class CreateProductImageUseCase(UseCase):
    async def __call__(self, command: CreateProductImageCommand) -> ProductImageResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateProductImageUseCase(UseCase):
    async def __call__(self, command: UpdateProductImageCommand) -> ProductImageResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteProductImageUseCase(UseCase):
    async def __call__(self, command: DeleteProductImageCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateProductImageUseCase",
    "UpdateProductImageUseCase",
    "DeleteProductImageUseCase",
]
