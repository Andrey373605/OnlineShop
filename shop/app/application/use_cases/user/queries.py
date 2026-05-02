
from shop.app.application.dto.commands import GetUserByIdCommand, ListUsersCommand
from shop.app.application.dto.responses import UserResponse, ListUsersResponse
from shop.app.application.use_cases.base import UseCase

class GetUserByIdUseCase(UseCase):
    async def __call__(self, command: GetUserByIdCommand) -> UserResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListUsersUseCase(UseCase):
    async def __call__(self, command: ListUsersCommand) -> ListUsersResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetUserByIdUseCase",
    "ListUsersUseCase",
]
