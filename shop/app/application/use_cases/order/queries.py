
from shop.app.application.dto.commands import GetOrderByIdCommand, ListOrdersCommand
from shop.app.application.dto.responses import OrderResponse, ListOrdersResponse
from shop.app.application.use_cases.base import UseCase

class GetOrderByIdUseCase(UseCase):
    async def __call__(self, command: GetOrderByIdCommand) -> OrderResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListOrdersUseCase(UseCase):
    async def __call__(self, command: ListOrdersCommand) -> ListOrdersResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetOrderByIdUseCase",
    "ListOrdersUseCase",
]
