from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_mongo_db(request: Request) -> AsyncIOMotorDatabase:
    """Выдаёт MongoDB-базу из app.state (устанавливается в lifespan)."""
    return request.app.state.mongo_db
