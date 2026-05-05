
from shop.app.application.dto.commands import GetProductVariantDetailsByIdCommand, ListProductVariantDetailsCommand
from shop.app.application.dto.responses import ProductVariantDetailsResponse, ListProductVariantDetailsResponse
from shop.app.application.use_cases.base import UseCase

class GetProductVariantDetailsByIdUseCase(UseCase):
    async def __call__(self, command: GetProductVariantDetailsByIdCommand) -> ProductVariantDetailsResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListProductVariantDetailsUseCase(UseCase):
    async def __call__(self, command: ListProductVariantDetailsCommand) -> ListProductVariantDetailsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetProductVariantDetailsByIdUseCase",
    "ListProductVariantDetailsUseCase",
]
