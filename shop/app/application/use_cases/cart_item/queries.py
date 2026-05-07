from shop.app.application.dto.commands import GetCartItemByIdCommand, ListCartItemsCommand
from shop.app.application.dto.responses import CartItemResponse, ListCartItemsResponse
from shop.app.application.use_cases.base import UseCase


class GetCartItemByIdUseCase(UseCase):
    async def __call__(self, command: GetCartItemByIdCommand) -> CartItemResponse | None:
        raise NotImplementedError("Use case is not implemented yet")


class ListCartItemsUseCase(UseCase):
    async def __call__(self, command: ListCartItemsCommand) -> ListCartItemsResponse:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "GetCartItemByIdUseCase",
    "ListCartItemsUseCase",
]
