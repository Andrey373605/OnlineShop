import json

from shop.app.repositories.protocols import UnitOfWork
from shop.app.schemas.analytics_schemas import StatsOut
from shop.app.services.cache_service import CacheService


CACHE_KEY_STATS = "analytics:stats"


class AnalyticsService:
    """Сервис аналитики: агрегированные данные с кэшированием в Redis."""

    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        cache_ttl_seconds: int,
    ):
        self.uow = uow
        self.cache = cache
        self._cache_ttl = cache_ttl_seconds

    async def get_stats(self) -> StatsOut:
        cached = await self.cache.get_value(CACHE_KEY_STATS)
        if cached is not None:
            data = json.loads(cached)
            return StatsOut(**data)

        async with self.uow as uow:
            total_orders = await uow.orders.get_total()
            total_users = await uow.users.get_total()
            total_products = await uow.products.get_total()

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
        await self.cache.delete(CACHE_KEY_STATS)
