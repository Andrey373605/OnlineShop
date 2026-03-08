from fastapi import Request
from shop.app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_mongo_db(request: Request) -> AsyncIOMotorDatabase:
    client = request.app.state.mongo_client
    return client[settings.MONGODB_DB]
