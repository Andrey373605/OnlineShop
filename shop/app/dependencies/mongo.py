from fastapi import Request
from shop.app.core.config import settings

async def get_mongo_db(request: Request):
    client = request.app.state.mongo_client
    return client[settings.MONGODB_DB]
