from fastapi import HTTPException, status

from shop.app.repositories.product_repository import ProductRepository
from shop.app.repositories.review_repository import ReviewRepository
from shop.app.schemas.review_schemas import ReviewCreate, ReviewOut, ReviewUpdate


class ReviewService:
    def __init__(
        self,
        review_repo: ReviewRepository,
        product_repo: ProductRepository,
    ) -> None:
        self.review_repo = review_repo
        self.product_repo = product_repo

    async def list_reviews(self, limit: int, offset: int) -> list[ReviewOut]:
        return await self.review_repo.get_all(limit=limit, offset=offset)

    async def get_review_by_id(self, review_id: int) -> ReviewOut:
        return await self._get_review_or_404(review_id)

    async def create_review(
        self,
        user_id: int,
        data: ReviewCreate,
    ) -> ReviewOut:
        self._validate_rating_value(data.rating)
        await self._ensure_product_exists(data.product_id)
        existing = await self.review_repo.get_by_user_and_product(
            user_id=user_id,
            product_id=data.product_id,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review for this product already exists",
            )

        payload = data.model_dump()
        payload["user_id"] = user_id
        review_id = await self.review_repo.create(payload)
        return await self._get_review_or_404(review_id)

    async def update_review(
        self,
        review_id: int,
        user_id: int,
        data: ReviewUpdate,
        is_admin: bool = False,
    ) -> ReviewOut:
        review = await self._get_review_or_404(review_id)
        self._ensure_author_or_admin(review.user_id, user_id, is_admin)

        if data.rating is not None:
            self._validate_rating_value(data.rating)

        success = await self.review_repo.update(
            review_id,
            data.model_dump(exclude_unset=True),
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update review",
            )
        return await self._get_review_or_404(review_id)

    async def delete_review(
        self,
        review_id: int,
        user_id: int,
        is_admin: bool = False,
    ) -> None:
        review = await self._get_review_or_404(review_id)
        self._ensure_author_or_admin(review.user_id, user_id, is_admin)

        success = await self.review_repo.delete(review_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete review",
            )

    async def _ensure_product_exists(self, product_id: int) -> None:
        exists = await self.product_repo.exists_product_with_id(product_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

    async def _get_review_or_404(self, review_id: int) -> ReviewOut:
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return review

    @staticmethod
    def _ensure_author_or_admin(
        review_user_id: int,
        current_user_id: int,
        is_admin: bool,
    ) -> None:
        if not (is_admin or review_user_id == current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to modify this review",
            )

    @staticmethod
    def _validate_rating_value(value: int) -> None:
        if value < 1 or value > 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Rating must be between 1 and 5",
            )


