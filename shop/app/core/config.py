from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


def _default_instance_id() -> str:
    return uuid4().hex[:12]


class Settings(BaseSettings):
    # Instance identification (auto-generated per process when not set)
    INSTANCE_ID: str = ""

    # Database settings
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # FastAPI settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # MongoDB settings
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_DB: str

    # Auth settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Role ID for new registrations (e.g. 2 = "user"). Must exist in roles table.
    DEFAULT_ADMIN_ROLE_ID: int = 1
    DEFAULT_USER_ROLE_ID: int = 2

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Failed login attempts
    MAX_FAILED_ATTEMPTS: int = 3
    BLOCK_TIME_MINUTES: int = 2

    # Cache TTL
    ROLES_CACHE_TTL_SECONDS: int = 300
    USERS_CACHE_TTL_SECONDS: int = 120
    CATEGORIES_CACHE_TTL_SECONDS: int = 300
    PRODUCTS_CACHE_TTL_SECONDS: int = 120
    ANALYTICS_CACHE_TTL_SECONDS: int = 60
    USER_SESSION_CACHE_TTL_SECONDS: int = 1800 

    # Minio settings
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET: str = "shop"
    MINIO_USE_SSL: bool = False

    # Event log retention (MongoDB TTL)
    EVENT_LOG_TTL_DAYS: int = 30

    # IANA-имя пояса для меток времени в логах (например Europe/Moscow, UTC)
    EVENT_LOG_TIMEZONE: str = "UTC"

    SECONDS_IN_MINUTE: int = 60

    @field_validator("EVENT_LOG_TIMEZONE")
    @classmethod
    def validate_event_log_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError as e:
            raise ValueError(f"Invalid EVENT_LOG_TIMEZONE: {v!r}") from e
        return v

    @property
    def event_log_tz(self) -> ZoneInfo:
        return ZoneInfo(self.EVENT_LOG_TIMEZONE)

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"

    @property
    def MINIO_URL(self) -> str:
        scheme = "https" if self.MINIO_USE_SSL else "http"
        return f"{scheme}://{self.MINIO_HOST}:{self.MINIO_PORT}"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


# Глобальный экземпляр настроек
settings = Settings()

if not settings.INSTANCE_ID:
    settings.INSTANCE_ID = _default_instance_id()
