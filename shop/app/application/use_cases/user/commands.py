
from shop.app.application.dto.commands import CreateUserCommand, UpdateUserCommand, DeleteUserCommand, AssignRoleToUserCommand, RevokeRoleFromUserCommand
from shop.app.application.dto.responses import UserResponse
from shop.app.application.use_cases.base import UseCase

class CreateUserUseCase(UseCase):
    async def __call__(self, command: CreateUserCommand) -> UserResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateUserUseCase(UseCase):
    async def __call__(self, command: UpdateUserCommand) -> UserResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteUserUseCase(UseCase):
    async def __call__(self, command: DeleteUserCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

class AssignRoleToUserUseCase(UseCase):
    async def __call__(self, command: AssignRoleToUserCommand) -> UserResponse:
        raise NotImplementedError("Use case is not implemented yet")

class RevokeRoleFromUserUseCase(UseCase):
    async def __call__(self, command: RevokeRoleFromUserCommand) -> UserResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateUserUseCase",
    "UpdateUserUseCase",
    "DeleteUserUseCase",
    "AssignRoleToUserUseCase",
    "RevokeRoleFromUserUseCase",
]
