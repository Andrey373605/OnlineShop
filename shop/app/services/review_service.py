from shop.app.core.exceptions import (
    DomainValidationError,
)
from shop.app.models.schemas import ReviewCreate, ReviewOut, ReviewUpdate
from shop.app.repositories.protocols import UnitOfWork


class ReviewService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def list_reviews(self, limit: int, offset: int) -> list[ReviewOut]:
        async with self._uow as uow:
            return await uow.reviews.get_all(limit=limit, offset=offset)

    async def get_review_by_id(self, review_id: int) -> ReviewOut:
        async with self._uow as uow:
            return await uow.reviews.get_by_id(review_id)

    async def create_review(
        self,
        user_id: int,
        data: ReviewCreate,
    ) -> ReviewOut:
        self._validate_rating_value(data.rating)
        async with self._uow as uow:
            review = await uow.reviews.create(data)
            await uow.commit()
            return review

    async def update_review(
        self,
        review_id: int,
        user_id: int,
        data: ReviewUpdate,
        is_admin: bool = False,
    ) -> ReviewOut:
        if data.rating is not None:
            self._validate_rating_value(data.rating)

        async with self._uow as uow:
            review = await uow.reviews.get_by_id(review_id)
            self._ensure_author_or_admin(review.user_id, user_id, is_admin)

            review = await uow.reviews.update(
                review_id,
                data.model_dump(exclude_unset=True),
            )

            await uow.commit()
            return review

    async def delete_review(
        self,
        review_id: int,
        user_id: int,
        is_admin: bool = False,
    ) -> None:
        async with self._uow as uow:
            review = await uow.reviews.get_by_id(review_id)
            self._ensure_author_or_admin(review.user_id, user_id, is_admin)

            await uow.reviews.delete(review_id)
            await uow.commit()

    @staticmethod
    def _ensure_author_or_admin(
        review_user_id: int,
        current_user_id: int,
        is_admin: bool,
    ) -> None:
        if not (is_admin or review_user_id == current_user_id):
            raise Exception("Not enough permissions to modify this review")

    @staticmethod
    def _validate_rating_value(value: int) -> None:
        if value < 1 or value > 5:
            raise DomainValidationError("Rating must be between 1 and 5")
