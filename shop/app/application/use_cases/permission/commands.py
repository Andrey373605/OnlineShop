
from shop.app.application.dto.commands import CreatePermissionCommand, UpdatePermissionCommand, DeletePermissionCommand
from shop.app.application.dto.responses import PermissionResponse
from shop.app.application.use_cases.base import UseCase

class CreatePermissionUseCase(UseCase):
    async def __call__(self, command: CreatePermissionCommand) -> PermissionResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdatePermissionUseCase(UseCase):
    async def __call__(self, command: UpdatePermissionCommand) -> PermissionResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeletePermissionUseCase(UseCase):
    async def __call__(self, command: DeletePermissionCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreatePermissionUseCase",
    "UpdatePermissionUseCase",
    "DeletePermissionUseCase",
]
