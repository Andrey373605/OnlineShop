
from shop.app.application.dto.commands import GetRoleByIdCommand, ListRolesCommand
from shop.app.application.dto.responses import RoleResponse, ListRolesResponse
from shop.app.application.use_cases.base import UseCase

class GetRoleByIdUseCase(UseCase):
    async def __call__(self, command: GetRoleByIdCommand) -> RoleResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListRolesUseCase(UseCase):
    async def __call__(self, command: ListRolesCommand) -> ListRolesResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetRoleByIdUseCase",
    "ListRolesUseCase",
]
