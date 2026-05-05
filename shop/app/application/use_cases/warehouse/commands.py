
from shop.app.application.dto.commands import CreateWarehouseCommand, UpdateWarehouseCommand, DeleteWarehouseCommand
from shop.app.application.dto.responses import WarehouseResponse
from shop.app.application.use_cases.base import UseCase

class CreateWarehouseUseCase(UseCase):
    async def __call__(self, command: CreateWarehouseCommand) -> WarehouseResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateWarehouseUseCase(UseCase):
    async def __call__(self, command: UpdateWarehouseCommand) -> WarehouseResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteWarehouseUseCase(UseCase):
    async def __call__(self, command: DeleteWarehouseCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateWarehouseUseCase",
    "UpdateWarehouseUseCase",
    "DeleteWarehouseUseCase",
]
