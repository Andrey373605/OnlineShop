from shop.app.core.config import settings
from shop.app.services.cache_service import CacheService, CacheServiceConfig


async def create_cache_service() -> CacheService:
    """Создать и подключить CacheService. Вызывается из lifespan."""
    cache = CacheService(CacheServiceConfig.from_settings(settings))
    await cache.connect()
    return cache
