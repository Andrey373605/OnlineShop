
from shop.app.application.dto.commands import CreateStockMovementCommand, UpdateStockMovementCommand, DeleteStockMovementCommand, ReserveStockCommand, ReleaseStockCommand, TransferStockCommand
from shop.app.application.dto.responses import StockMovementResponse
from shop.app.application.use_cases.base import UseCase

class CreateStockMovementUseCase(UseCase):
    async def __call__(self, command: CreateStockMovementCommand) -> StockMovementResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateStockMovementUseCase(UseCase):
    async def __call__(self, command: UpdateStockMovementCommand) -> StockMovementResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteStockMovementUseCase(UseCase):
    async def __call__(self, command: DeleteStockMovementCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

class ReserveStockUseCase(UseCase):
    async def __call__(self, command: ReserveStockCommand) -> StockMovementResponse:
        raise NotImplementedError("Use case is not implemented yet")

class ReleaseStockUseCase(UseCase):
    async def __call__(self, command: ReleaseStockCommand) -> StockMovementResponse:
        raise NotImplementedError("Use case is not implemented yet")

class TransferStockUseCase(UseCase):
    async def __call__(self, command: TransferStockCommand) -> StockMovementResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateStockMovementUseCase",
    "UpdateStockMovementUseCase",
    "DeleteStockMovementUseCase",
    "ReserveStockUseCase",
    "ReleaseStockUseCase",
    "TransferStockUseCase",
]
