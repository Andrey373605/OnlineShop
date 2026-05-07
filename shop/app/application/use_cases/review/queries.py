
from shop.app.application.dto.commands import GetReviewByIdCommand, ListReviewsCommand
from shop.app.application.dto.responses import ReviewResponse, ListReviewsResponse
from shop.app.application.use_cases.base import UseCase

class GetReviewByIdUseCase(UseCase):
    async def __call__(self, command: GetReviewByIdCommand) -> ReviewResponse | None:
        raise NotImplementedError("Use case is not implemented yet")

class ListReviewsUseCase(UseCase):
    async def __call__(self, command: ListReviewsCommand) -> ListReviewsResponse:
        raise NotImplementedError("Use case is not implemented yet")

__all__ = [
    "GetReviewByIdUseCase",
    "ListReviewsUseCase",
]
