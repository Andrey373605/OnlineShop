
from typing import cast

from shop.app.domain.errors import (
    DomainValidationError,
    EmptyReviewTitleError,
    InvalidRatingError,
    ReviewTitleTooLongError,
)

_MIN_RATING = 1
_MAX_RATING = 5
_MAX_TITLE_LEN = 200
_MAX_DESCRIPTION_LEN = 10_000


class ReviewTitle(str):
    def __new__(cls, value: str) -> ReviewTitle:
        if not isinstance(value, str):
            raise EmptyReviewTitleError("Review title must be a string")
        clean = value.strip()
        if not clean:
            raise EmptyReviewTitleError("Review title cannot be empty")
        if len(clean) > _MAX_TITLE_LEN:
            raise ReviewTitleTooLongError("Review title is too long")
        return cast(ReviewTitle, str.__new__(cls, clean))


class ReviewDescription(str):
    def __new__(cls, value: str) -> ReviewDescription:
        if not isinstance(value, str):
            raise DomainValidationError("Review description must be a string")
        clean = value.strip()
        if not clean:
            raise DomainValidationError("Review description cannot be empty")
        if len(clean) > _MAX_DESCRIPTION_LEN:
            raise DomainValidationError("Review description is too long")
        return cast(ReviewDescription, str.__new__(cls, clean))


class Rating(int):
    def __new__(cls, value: int) -> Rating:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidRatingError("Rating must be an integer")
        if value < _MIN_RATING or value > _MAX_RATING:
            raise InvalidRatingError(
                f"Rating must be between {_MIN_RATING} and {_MAX_RATING}",
            )
        return cast(Rating, int.__new__(cls, value))


def normalize_review_description(value: str | None) -> ReviewDescription | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise DomainValidationError("Review description must be a string or null")
    stripped = value.strip()
    if not stripped:
        return None
    return ReviewDescription(stripped)


__all__ = ["ReviewTitle", "ReviewDescription", "Rating", "normalize_review_description"]
