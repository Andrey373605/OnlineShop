
from shop.app.application.dto.commands import GetProductDetailsByIdCommand, ListProductDetailsCommand
from shop.app.application.dto.responses import ProductDetailsResponse, ListProductDetailsResponse
from shop.app.application.use_cases.base import UseCase

class GetProductDetailsByIdUseCase(UseCase):
    async def __call__(self, command: GetProductDetailsByIdCommand) -> ProductDetailsResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListProductDetailsUseCase(UseCase):
    async def __call__(self, command: ListProductDetailsCommand) -> ListProductDetailsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetProductDetailsByIdUseCase",
    "ListProductDetailsUseCase",
]
