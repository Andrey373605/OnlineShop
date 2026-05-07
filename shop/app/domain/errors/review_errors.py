
from shop.app.domain.errors.base import DomainError


class EmptyReviewTitleError(DomainError):
    """Raised when review title is empty."""


class ReviewTitleTooLongError(DomainError):
    """Raised when review title exceeds max length."""


class InvalidRatingError(DomainError):
    """Raised when rating is outside supported range."""
