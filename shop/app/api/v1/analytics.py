from fastapi import APIRouter, Depends

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_analytics_service
from shop.app.schemas.analytics_schemas import StatsOut
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.analytics_service import AnalyticsService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats", response_model=StatsOut)
async def get_stats(
    current_user: UserOut = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> StatsOut:
    """
    Результаты аналитического запроса: количество заказов, пользователей и товаров.
    Ответ кэшируется в Redis (TTL задаётся в настройках).
    """
    _ensure_admin(current_user)
    return await analytics_service.get_stats()
