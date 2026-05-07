from shop.app.application.dto.commands import (
    CreateBrandCommand,
    UpdateBrandCommand,
    DeleteBrandCommand,
)
from shop.app.application.dto.responses import BrandResponse
from shop.app.application.use_cases.base import UseCase


class CreateBrandUseCase(UseCase):
    async def __call__(self, command: CreateBrandCommand) -> BrandResponse:
        raise NotImplementedError("Use case is not implemented yet")


class UpdateBrandUseCase(UseCase):
    async def __call__(self, command: UpdateBrandCommand) -> BrandResponse:
        raise NotImplementedError("Use case is not implemented yet")


class DeleteBrandUseCase(UseCase):
    async def __call__(self, command: DeleteBrandCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")


__all__ = [
    "CreateBrandUseCase",
    "UpdateBrandUseCase",
    "DeleteBrandUseCase",
]
