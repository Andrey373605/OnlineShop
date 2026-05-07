from fastapi import Request

from shop.app.core.state import get_app_state
from shop.app.services.cache_service import CacheService


async def get_cache_service(request: Request) -> CacheService:
    return get_app_state(request).cache_service
