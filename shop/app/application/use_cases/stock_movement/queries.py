
from shop.app.application.dto.commands import GetStockMovementByIdCommand, ListStockMovementsCommand
from shop.app.application.dto.responses import StockMovementResponse, ListStockMovementsResponse
from shop.app.application.use_cases.base import UseCase

class GetStockMovementByIdUseCase(UseCase):
    async def __call__(self, command: GetStockMovementByIdCommand) -> StockMovementResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListStockMovementsUseCase(UseCase):
    async def __call__(self, command: ListStockMovementsCommand) -> ListStockMovementsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetStockMovementByIdUseCase",
    "ListStockMovementsUseCase",
]
