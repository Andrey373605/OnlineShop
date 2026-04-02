from shop.app.core.exceptions import (
    AlreadyExistsError,
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
    PermissionDeniedError,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.models.schemas import ReviewCreate, ReviewOut, ReviewUpdate


class ReviewService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def list_reviews(self, limit: int, offset: int) -> list[ReviewOut]:
        async with self._uow as uow:
            return await uow.reviews.get_all(limit=limit, offset=offset)

    async def get_review_by_id(self, review_id: int) -> ReviewOut:
        async with self._uow as uow:
            return await self._get_review_or_raise(uow, review_id)

    async def create_review(
        self,
        user_id: int,
        data: ReviewCreate,
    ) -> ReviewOut:
        self._validate_rating_value(data.rating)
        async with self._uow as uow:
            if not await uow.products.exists_product_with_id(data.product_id):
                raise NotFoundError("Product")

            existing = await uow.reviews.get_by_user_and_product(
                user_id=user_id,
                product_id=data.product_id,
            )
            if existing:
                raise AlreadyExistsError(
                    "Review", "Review for this product already exists"
                )

            payload = data.model_dump()
            payload["user_id"] = user_id
            review_id = await uow.reviews.create(payload)
            review = await self._get_review_or_raise(uow, review_id)
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
            review = await self._get_review_or_raise(uow, review_id)
            self._ensure_author_or_admin(review.user_id, user_id, is_admin)

            success = await uow.reviews.update(
                review_id,
                data.model_dump(exclude_unset=True),
            )
            if not success:
                raise OperationFailedError("Failed to update review")

            review = await self._get_review_or_raise(uow, review_id)
            await uow.commit()
            return review

    async def delete_review(
        self,
        review_id: int,
        user_id: int,
        is_admin: bool = False,
    ) -> None:
        async with self._uow as uow:
            review = await self._get_review_or_raise(uow, review_id)
            self._ensure_author_or_admin(review.user_id, user_id, is_admin)

            success = await uow.reviews.delete(review_id)
            if not success:
                raise OperationFailedError("Failed to delete review")
            await uow.commit()

    @staticmethod
    async def _get_review_or_raise(uow: UnitOfWork, review_id: int) -> ReviewOut:
        review = await uow.reviews.get_by_id(review_id)
        if not review:
            raise NotFoundError("Review")
        return review

    @staticmethod
    def _ensure_author_or_admin(
        review_user_id: int,
        current_user_id: int,
        is_admin: bool,
    ) -> None:
        if not (is_admin or review_user_id == current_user_id):
            raise PermissionDeniedError("Not enough permissions to modify this review")

    @staticmethod
    def _validate_rating_value(value: int) -> None:
        if value < 1 or value > 5:
            raise DomainValidationError("Rating must be between 1 and 5")
