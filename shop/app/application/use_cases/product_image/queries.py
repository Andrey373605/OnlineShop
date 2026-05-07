
from shop.app.application.dto.commands import GetProductImageByIdCommand, ListProductImagesCommand
from shop.app.application.dto.responses import ProductImageResponse, ListProductImagesResponse
from shop.app.application.use_cases.base import UseCase

class GetProductImageByIdUseCase(UseCase):
    async def __call__(self, command: GetProductImageByIdCommand) -> ProductImageResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListProductImagesUseCase(UseCase):
    async def __call__(self, command: ListProductImagesCommand) -> ListProductImagesResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetProductImageByIdUseCase",
    "ListProductImagesUseCase",
]
