from fastapi import Request

from shop.app.core.ports.storage import StoragePort
from shop.app.core.state import get_app_state


async def get_storage_service(request: Request) -> StoragePort:
    return get_app_state(request).storage
