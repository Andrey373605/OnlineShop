import json

from shop.app.repositories.order_repository import OrderRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.repositories.user_repository import UserRepository
from shop.app.schemas.analytics_schemas import StatsOut
from shop.app.services.cache_service import CacheService


CACHE_KEY_STATS = "analytics:stats"


class AnalyticsService:
    """Сервис аналитики: агрегированные данные с кэшированием в Redis."""

    def __init__(
        self,
        order_repo: OrderRepository,
        user_repo: UserRepository,
        product_repo: ProductRepository,
        cache: CacheService,
        cache_ttl_seconds: int,
    ):
        self.order_repo = order_repo
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.cache = cache
        self._cache_ttl = cache_ttl_seconds

    async def get_stats(self) -> StatsOut:
        """
        Возвращает сводную статистику (количество заказов, пользователей, товаров).
        Результат кэшируется в Redis для снижения нагрузки на БД.
        """
        cached = await self.cache.get_value(CACHE_KEY_STATS)
        if cached is not None:
            data = json.loads(cached)
            return StatsOut(**data)

        total_orders = await self.order_repo.get_total()
        total_users = await self.user_repo.get_total()
        total_products = await self.product_repo.get_total()

        stats = StatsOut(
            total_orders=total_orders,
            total_users=total_users,
            total_products=total_products,
        )
        await self.cache.set_value(
            CACHE_KEY_STATS,
            stats.model_dump_json(),
            ttl_seconds=self._cache_ttl,
        )
        return stats

    async def invalidate_stats_cache(self) -> None:
        """Сбросить кэш аналитики (вызывать при изменении заказов/пользователей/товаров)."""
        await self.cache.delete(CACHE_KEY_STATS)
