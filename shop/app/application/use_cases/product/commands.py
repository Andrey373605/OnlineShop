
from shop.app.application.dto.commands import CreateProductCommand, UpdateProductCommand, DeleteProductCommand, PublishProductCommand, ArchiveProductCommand
from shop.app.application.dto.responses import ProductResponse
from shop.app.application.use_cases.base import UseCase

class CreateProductUseCase(UseCase):
    async def __call__(self, command: CreateProductCommand) -> ProductResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateProductUseCase(UseCase):
    async def __call__(self, command: UpdateProductCommand) -> ProductResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteProductUseCase(UseCase):
    async def __call__(self, command: DeleteProductCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

class PublishProductUseCase(UseCase):
    async def __call__(self, command: PublishProductCommand) -> ProductResponse:
        raise NotImplementedError("Use case is not implemented yet")

class ArchiveProductUseCase(UseCase):
    async def __call__(self, command: ArchiveProductCommand) -> ProductResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateProductUseCase",
    "UpdateProductUseCase",
    "DeleteProductUseCase",
    "PublishProductUseCase",
    "ArchiveProductUseCase",
]
