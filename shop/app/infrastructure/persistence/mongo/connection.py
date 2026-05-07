from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from shop.app.core.ports.base import Lifecycle
from shop.app.core.ports.client_provider import ClientProvider


class MongoInfrastructure(Lifecycle, ClientProvider):
    def __init__(self, *, url: str):
        self._url = url
        self._client: MongoClient | None = None

    def connect(self) -> None:
        if self._client is not None:
            return
        self._client = AsyncIOMotorClient(self._url)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def get_client(self):
        if self._client is None:
            raise RuntimeError("Mongo client is not connected")
        return self._client
