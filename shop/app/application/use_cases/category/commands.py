
from shop.app.application.dto.commands import CreateCategoryCommand, UpdateCategoryCommand, DeleteCategoryCommand
from shop.app.application.dto.responses import CategoryResponse
from shop.app.application.use_cases.base import UseCase

class CreateCategoryUseCase(UseCase):
    async def __call__(self, command: CreateCategoryCommand) -> CategoryResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateCategoryUseCase(UseCase):
    async def __call__(self, command: UpdateCategoryCommand) -> CategoryResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteCategoryUseCase(UseCase):
    async def __call__(self, command: DeleteCategoryCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateCategoryUseCase",
    "UpdateCategoryUseCase",
    "DeleteCategoryUseCase",
]
