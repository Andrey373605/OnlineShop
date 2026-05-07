
from shop.app.application.dto.commands import GetCategoryByIdCommand, ListCategoriesCommand
from shop.app.application.dto.responses import CategoryResponse, ListCategoriesResponse
from shop.app.application.use_cases.base import UseCase

class GetCategoryByIdUseCase(UseCase):
    async def __call__(self, command: GetCategoryByIdCommand) -> CategoryResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListCategoriesUseCase(UseCase):
    async def __call__(self, command: ListCategoriesCommand) -> ListCategoriesResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetCategoryByIdUseCase",
    "ListCategoriesUseCase",
]
