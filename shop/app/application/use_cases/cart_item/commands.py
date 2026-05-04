from shop.app.application.dto.commands import (
    CreateCartItemCommand,
    UpdateCartItemCommand,
    DeleteCartItemCommand,
)
from shop.app.application.dto.responses import CartItemResponse
from shop.app.application.use_cases.base import UseCase


class CreateCartItemUseCase(UseCase):
    async def __call__(self, command: CreateCartItemCommand) -> CartItemResponse:
        raise NotImplementedError("Use case is not implemented yet")


class UpdateCartItemUseCase(UseCase):
    async def __call__(self, command: UpdateCartItemCommand) -> CartItemResponse:
        raise NotImplementedError("Use case is not implemented yet")


class DeleteCartItemUseCase(UseCase):
    async def __call__(self, command: DeleteCartItemCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "CreateCartItemUseCase",
    "UpdateCartItemUseCase",
    "DeleteCartItemUseCase",
]
