from shop.app.application.dto.commands import GetBrandByIdCommand, ListBrandsCommand
from shop.app.application.dto.responses import BrandResponse, ListBrandsResponse
from shop.app.application.use_cases.base import UseCase


class GetBrandByIdUseCase(UseCase):
    async def __call__(self, command: GetBrandByIdCommand) -> BrandResponse | None:
        raise NotImplementedError("Use case is not implemented yet")


class ListBrandsUseCase(UseCase):
    async def __call__(self, command: ListBrandsCommand) -> ListBrandsResponse:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "GetBrandByIdUseCase",
    "ListBrandsUseCase",
]
