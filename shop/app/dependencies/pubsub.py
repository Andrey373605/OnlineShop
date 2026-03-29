from fastapi import Request

from shop.app.services.pubsub_service import PubSubService


async def get_pubsub_service(request: Request) -> PubSubService:
    return request.app.state.pubsub_service
