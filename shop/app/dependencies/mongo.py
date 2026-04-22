from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from shop.app.core.state import get_app_state


async def get_mongo_db(request: Request) -> AsyncIOMotorDatabase:
    """Выдаёт MongoDB-базу из типизированного контейнера app.state.ext."""
    return get_app_state(request).mongo_db
