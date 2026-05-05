
from shop.app.application.dto.commands import CreatePriceCommand, UpdatePriceCommand, DeletePriceCommand
from shop.app.application.dto.responses import PriceResponse
from shop.app.application.use_cases.base import UseCase

class CreatePriceUseCase(UseCase):
    async def __call__(self, command: CreatePriceCommand) -> PriceResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdatePriceUseCase(UseCase):
    async def __call__(self, command: UpdatePriceCommand) -> PriceResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeletePriceUseCase(UseCase):
    async def __call__(self, command: DeletePriceCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreatePriceUseCase",
    "UpdatePriceUseCase",
    "DeletePriceUseCase",
]
