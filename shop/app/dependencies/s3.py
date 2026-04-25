from fastapi import Request

from shop.app.core.ports.storage import StoragePort, StorageReadinessPort
from shop.app.core.state import get_app_state


async def get_storage_service(request: Request) -> StoragePort:
    return get_app_state(request).storage


async def get_storage_readiness(request: Request) -> StorageReadinessPort:
    return get_app_state(request).storage_readiness
