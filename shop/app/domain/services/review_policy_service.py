
from collections.abc import Sequence

from shop.app.domain import Order, Review, User


class ReviewPolicyDomainService:
    """Applies review eligibility and moderation domain policies."""

    def ensure_review_allowed(
        self,
        user: User,
        review: Review,
        user_orders: Sequence[Order],
    ) -> None:
        """Validate user eligibility to leave a review for purchased product."""
        raise NotImplementedError("Domain service is not implemented yet")

    def should_flag_for_moderation(self, review: Review) -> bool:
        """Return moderation flag for review according to domain policy."""
        raise NotImplementedError("Domain service is not implemented yet")


__all__ = ["ReviewPolicyDomainService"]

