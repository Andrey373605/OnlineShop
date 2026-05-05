"""Non-domain (technical / legacy SQL) persistence ports."""

from shop.app.application.interfaces.repositories.cart_item_repository import CartItemRepository
from shop.app.application.interfaces.persistence.event_log_analytics_repository import (
    EventLogAnalyticsRepository,
)
from shop.app.application.interfaces.persistence.event_log_repository import EventLogRepository
from shop.app.application.interfaces.repositories.order_item_repository import OrderItemRepository
from shop.app.application.interfaces.repositories.product_specification_repository import (
    ProductSpecificationRepository,
)
from shop.app.application.interfaces.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)

__all__ = [
    "CartItemRepository",
    "EventLogAnalyticsRepository",
    "EventLogRepository",
    "OrderItemRepository",
    "ProductSpecificationRepository",
    "RefreshTokenRepository",
]
