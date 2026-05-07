
from shop.app.application.dto.commands import GetWarehouseByIdCommand, ListWarehousesCommand
from shop.app.application.dto.responses import WarehouseResponse, ListWarehousesResponse
from shop.app.application.use_cases.base import UseCase

class GetWarehouseByIdUseCase(UseCase):
    async def __call__(self, command: GetWarehouseByIdCommand) -> WarehouseResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListWarehousesUseCase(UseCase):
    async def __call__(self, command: ListWarehousesCommand) -> ListWarehousesResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetWarehouseByIdUseCase",
    "ListWarehousesUseCase",
]
