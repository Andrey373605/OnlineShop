from fastapi import Request

from shop.app.core.state import get_app_state
from shop.app.services.pubsub_service import PubSubService


async def get_pubsub_service(request: Request) -> PubSubService:
    return get_app_state(request).pubsub_service
