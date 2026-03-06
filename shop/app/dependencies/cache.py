from fastapi import Request

from shop.app.services.cache_service import CacheService


def get_cache_service(request: Request) -> CacheService:
    return request.app.state.cache_service
