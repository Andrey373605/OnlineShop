"""Типизированный контейнер ресурсов приложения."""

from dataclasses import dataclass
from typing import cast

import asyncpg
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from shop.app.core.ports.base import HealthCheckPort
from shop.app.application.interfaces.services.files.file_storage import FileStoragePort
from depricated.services.cache_service import CacheService
from depricated.services.session_service import SessionService


@dataclass(slots=True)
class AppState:

    db_pool: asyncpg.Pool
    cache_service: CacheService
    mongo_client: AsyncIOMotorClient
    mongo_db: AsyncIOMotorDatabase
    session_service: SessionService
    storage: FileStoragePort
    storage_readiness: HealthCheckPort


def get_app_state(request: Request) -> AppState:
    return cast(AppState, request.app.state.ext)
