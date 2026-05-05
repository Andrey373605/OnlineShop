
from shop.app.application.dto.commands import GetPermissionByIdCommand, ListPermissionsCommand
from shop.app.application.dto.responses import PermissionResponse, ListPermissionsResponse
from shop.app.application.use_cases.base import UseCase

class GetPermissionByIdUseCase(UseCase):
    async def __call__(self, command: GetPermissionByIdCommand) -> PermissionResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListPermissionsUseCase(UseCase):
    async def __call__(self, command: ListPermissionsCommand) -> ListPermissionsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetPermissionByIdUseCase",
    "ListPermissionsUseCase",
]
