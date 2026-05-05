from shop.app.application.dto.commands import (
    CreateCartCommand,
    UpdateCartCommand,
    DeleteCartCommand,
    AddItemToCartCommand,
    RemoveItemFromCartCommand,
    ChangeCartItemQuantityCommand,
    ClearCartCommand,
)
from shop.app.application.dto.responses import CartResponse
from shop.app.application.use_cases.base import UseCase


class CreateCartUseCase(UseCase):
    async def __call__(self, command: CreateCartCommand) -> CartResponse:
        raise NotImplementedError("Use case is not implemented yet")


class UpdateCartUseCase(UseCase):
    async def __call__(self, command: UpdateCartCommand) -> CartResponse:
        raise NotImplementedError("Use case is not implemented yet")


class DeleteCartUseCase(UseCase):
    async def __call__(self, command: DeleteCartCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")


class AddItemToCartUseCase(UseCase):
    async def __call__(self, command: AddItemToCartCommand) -> CartResponse:
        raise NotImplementedError("Use case is not implemented yet")


class RemoveItemFromCartUseCase(UseCase):
    async def __call__(self, command: RemoveItemFromCartCommand) -> CartResponse:
        raise NotImplementedError("Use case is not implemented yet")


class ChangeCartItemQuantityUseCase(UseCase):
    async def __call__(self, command: ChangeCartItemQuantityCommand) -> CartResponse:
        raise NotImplementedError("Use case is not implemented yet")


class ClearCartUseCase(UseCase):
    async def __call__(self, command: ClearCartCommand) -> CartResponse:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "CreateCartUseCase",
    "UpdateCartUseCase",
    "DeleteCartUseCase",
    "AddItemToCartUseCase",
    "RemoveItemFromCartUseCase",
    "ChangeCartItemQuantityUseCase",
    "ClearCartUseCase",
]
