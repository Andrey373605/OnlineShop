from shop.app.application.dto.commands import GetCartByIdCommand, ListCartsCommand
from shop.app.application.dto.responses import CartResponse, ListCartsResponse
from shop.app.application.use_cases.base import UseCase


class GetCartByIdUseCase(UseCase):
    async def __call__(self, command: GetCartByIdCommand) -> CartResponse | None:
        raise NotImplementedError("Use case is not implemented yet")


class ListCartsUseCase(UseCase):
    async def __call__(self, command: ListCartsCommand) -> ListCartsResponse:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "GetCartByIdUseCase",
    "ListCartsUseCase",
]
