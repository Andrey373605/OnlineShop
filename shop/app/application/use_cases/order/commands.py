
from shop.app.application.dto.commands import CreateOrderCommand, UpdateOrderCommand, DeleteOrderCommand, PlaceOrderCommand, CancelOrderCommand, ChangeOrderStatusCommand
from shop.app.application.dto.responses import OrderResponse
from shop.app.application.use_cases.base import UseCase

class CreateOrderUseCase(UseCase):
    async def __call__(self, command: CreateOrderCommand) -> OrderResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateOrderUseCase(UseCase):
    async def __call__(self, command: UpdateOrderCommand) -> OrderResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteOrderUseCase(UseCase):
    async def __call__(self, command: DeleteOrderCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

class PlaceOrderUseCase(UseCase):
    async def __call__(self, command: PlaceOrderCommand) -> OrderResponse:
        raise NotImplementedError("Use case is not implemented yet")

class CancelOrderUseCase(UseCase):
    async def __call__(self, command: CancelOrderCommand) -> OrderResponse:
        raise NotImplementedError("Use case is not implemented yet")

class ChangeOrderStatusUseCase(UseCase):
    async def __call__(self, command: ChangeOrderStatusCommand) -> OrderResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateOrderUseCase",
    "UpdateOrderUseCase",
    "DeleteOrderUseCase",
    "PlaceOrderUseCase",
    "CancelOrderUseCase",
    "ChangeOrderStatusUseCase",
]
