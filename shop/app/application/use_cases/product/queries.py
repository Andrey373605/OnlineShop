
from shop.app.application.dto.commands import GetProductByIdCommand, ListProductsCommand
from shop.app.application.dto.responses import ProductResponse, ListProductsResponse
from shop.app.application.use_cases.base import UseCase

class GetProductByIdUseCase(UseCase):
    async def __call__(self, command: GetProductByIdCommand) -> ProductResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListProductsUseCase(UseCase):
    async def __call__(self, command: ListProductsCommand) -> ListProductsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetProductByIdUseCase",
    "ListProductsUseCase",
]
