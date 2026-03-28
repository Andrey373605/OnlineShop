from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from shop.app.core.config import settings


def create_mongo_client() -> AsyncIOMotorClient:
    """Создать MongoDB-клиент. Вызывается из lifespan, результат хранить в app.state.mongo_client."""
    return AsyncIOMotorClient(settings.MONGO_URL)


def get_mongo_database(client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    """Получить объект базы данных из клиента."""
    return client[settings.MONGODB_DB]


def close_mongo_client(client: AsyncIOMotorClient) -> None:
    """Закрыть клиент. Вызывается из lifespan при остановке приложения."""
    client.close()
