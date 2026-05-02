from datetime import datetime
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.value_objects.review_values import (
    Rating,
    ReviewDescription,
    ReviewTitle,
)
from shop.app.utils.get_utc_now import get_utc_now


class Review:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        product_id: UUID,
        title: ReviewTitle,
        description: ReviewDescription | None,
        rating: Rating,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._product_id = product_id
        self._title = title
        self._description = description
        self._rating = rating
        now = get_utc_now()
        self._created_at = created_at or now
        self._updated_at = updated_at or self._created_at

    @classmethod
    def create(
        cls,
        user_id: UUID,
        product_id: UUID,
        title: ReviewTitle,
        rating: Rating,
        description: ReviewDescription | None = None,
    ) -> "Review":
        return cls(
            id=uuid7(),
            user_id=user_id,
            product_id=product_id,
            title=title,
            description=description,
            rating=rating,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def product_id(self) -> UUID:
        return self._product_id

    @property
    def title(self) -> ReviewTitle:
        return self._title

    @property
    def description(self) -> ReviewDescription | None:
        return self._description

    @property
    def rating(self) -> Rating:
        return self._rating

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def change_title(self, new_title: ReviewTitle) -> None:
        self._title = new_title
        self._touch()

    def change_description(self, new_description: ReviewDescription | None) -> None:
        self._description = new_description
        self._touch()

    def change_rating(self, new_rating: Rating) -> None:
        self._rating = new_rating
        self._touch()

    def _touch(self) -> None:
        self._updated_at = get_utc_now()

    def __repr__(self) -> str:
        return f"<Review product={self._product_id} rating={self._rating} ({self._id})>"
