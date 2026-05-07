from shop.app.application.dto.commands import (
    CreateOrderItemCommand,
    UpdateOrderItemCommand,
    DeleteOrderItemCommand,
)
from shop.app.application.dto.responses import OrderItemResponse
from shop.app.application.use_cases.base import UseCase


class CreateOrderItemUseCase(UseCase):
    async def __call__(self, command: CreateOrderItemCommand) -> OrderItemResponse:
        raise NotImplementedError("Use case is not implemented yet")


class UpdateOrderItemUseCase(UseCase):
    async def __call__(self, command: UpdateOrderItemCommand) -> OrderItemResponse:
        raise NotImplementedError("Use case is not implemented yet")


class DeleteOrderItemUseCase(UseCase):
    async def __call__(self, command: DeleteOrderItemCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "CreateOrderItemUseCase",
    "UpdateOrderItemUseCase",
    "DeleteOrderItemUseCase",
]
