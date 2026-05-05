
from shop.app.application.dto.commands import CreateRoleCommand, UpdateRoleCommand, DeleteRoleCommand, GrantPermissionToRoleCommand, RevokePermissionFromRoleCommand
from shop.app.application.dto.responses import RoleResponse
from shop.app.application.use_cases.base import UseCase

class CreateRoleUseCase(UseCase):
    async def __call__(self, command: CreateRoleCommand) -> RoleResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateRoleUseCase(UseCase):
    async def __call__(self, command: UpdateRoleCommand) -> RoleResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteRoleUseCase(UseCase):
    async def __call__(self, command: DeleteRoleCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

class GrantPermissionToRoleUseCase(UseCase):
    async def __call__(self, command: GrantPermissionToRoleCommand) -> RoleResponse:
        raise NotImplementedError("Use case is not implemented yet")

class RevokePermissionFromRoleUseCase(UseCase):
    async def __call__(self, command: RevokePermissionFromRoleCommand) -> RoleResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateRoleUseCase",
    "UpdateRoleUseCase",
    "DeleteRoleUseCase",
    "GrantPermissionToRoleUseCase",
    "RevokePermissionFromRoleUseCase",
]
