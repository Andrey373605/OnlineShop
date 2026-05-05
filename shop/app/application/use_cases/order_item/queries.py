
from shop.app.application.dto.commands import GetOrderItemByIdCommand, ListOrderItemsCommand
from shop.app.application.dto.responses import OrderItemResponse, ListOrderItemsResponse
from shop.app.application.use_cases.base import UseCase

class GetOrderItemByIdUseCase(UseCase):
    async def __call__(self, command: GetOrderItemByIdCommand) -> OrderItemResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListOrderItemsUseCase(UseCase):
    async def __call__(self, command: ListOrderItemsCommand) -> ListOrderItemsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetOrderItemByIdUseCase",
    "ListOrderItemsUseCase",
]
