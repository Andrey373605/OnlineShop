"""Типизированный контейнер ресурсов приложения."""

from dataclasses import dataclass
from typing import cast

import asyncpg
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from shop.app.core.ports.base import HealthCheckPort
from shop.app.core.ports.file_storage import FileStoragePort
from shop.app.services.cache_service import CacheService
from shop.app.services.pubsub_service import PubSubService
from shop.app.services.session_service import SessionService


@dataclass(slots=True)
class AppState:

    db_pool: asyncpg.Pool
    cache_service: CacheService
    mongo_client: AsyncIOMotorClient
    mongo_db: AsyncIOMotorDatabase
    session_service: SessionService
    pubsub_service: PubSubService
    storage: FileStoragePort
    storage_readiness: HealthCheckPort


def get_app_state(request: Request) -> AppState:
    return cast(AppState, request.app.state.ext)
