
from shop.app.application.dto.commands import CreateProductDetailsCommand, UpdateProductDetailsCommand, DeleteProductDetailsCommand
from shop.app.application.dto.responses import ProductDetailsResponse
from shop.app.application.use_cases.base import UseCase

class CreateProductDetailsUseCase(UseCase):
    async def __call__(self, command: CreateProductDetailsCommand) -> ProductDetailsResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateProductDetailsUseCase(UseCase):
    async def __call__(self, command: UpdateProductDetailsCommand) -> ProductDetailsResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteProductDetailsUseCase(UseCase):
    async def __call__(self, command: DeleteProductDetailsCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateProductDetailsUseCase",
    "UpdateProductDetailsUseCase",
    "DeleteProductDetailsUseCase",
]
