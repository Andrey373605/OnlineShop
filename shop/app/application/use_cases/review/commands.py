
from shop.app.application.dto.commands import CreateReviewCommand, UpdateReviewCommand, DeleteReviewCommand
from shop.app.application.dto.responses import ReviewResponse
from shop.app.application.use_cases.base import UseCase

class CreateReviewUseCase(UseCase):
    async def __call__(self, command: CreateReviewCommand) -> ReviewResponse:
        raise NotImplementedError("Use case is not implemented yet")

class UpdateReviewUseCase(UseCase):
    async def __call__(self, command: UpdateReviewCommand) -> ReviewResponse:
        raise NotImplementedError("Use case is not implemented yet")

class DeleteReviewUseCase(UseCase):
    async def __call__(self, command: DeleteReviewCommand) -> None:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "CreateReviewUseCase",
    "UpdateReviewUseCase",
    "DeleteReviewUseCase",
]
