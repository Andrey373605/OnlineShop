
from shop.app.application.dto.commands import GetProductVariantByIdCommand, ListProductVariantsCommand
from shop.app.application.dto.responses import ProductVariantResponse, ListProductVariantsResponse
from shop.app.application.use_cases.base import UseCase

class GetProductVariantByIdUseCase(UseCase):
    async def __call__(self, command: GetProductVariantByIdCommand) -> ProductVariantResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListProductVariantsUseCase(UseCase):
    async def __call__(self, command: ListProductVariantsCommand) -> ListProductVariantsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetProductVariantByIdUseCase",
    "ListProductVariantsUseCase",
]
