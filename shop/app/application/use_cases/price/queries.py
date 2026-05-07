
from shop.app.application.dto.commands import GetPriceByIdCommand, ListPricesCommand
from shop.app.application.dto.responses import PriceResponse, ListPricesResponse
from shop.app.application.use_cases.base import UseCase

class GetPriceByIdUseCase(UseCase):
    async def __call__(self, command: GetPriceByIdCommand) -> PriceResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListPricesUseCase(UseCase):
    async def __call__(self, command: ListPricesCommand) -> ListPricesResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetPriceByIdUseCase",
    "ListPricesUseCase",
]
