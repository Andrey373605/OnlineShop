from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_DB: str

    # Auth settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Role ID for new registrations (e.g. 2 = "user"). Must exist in roles table.
    DEFAULT_USER_ROLE_ID: int = 2

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Failed login attempts
    MAX_FAILED_ATTEMPTS: int = 3
    BLOCK_TIME_MINUTES: int = 10

    # Cache TTL
    ROLES_CACHE_TTL_SECONDS: int = 300
    USERS_CACHE_TTL_SECONDS: int = 120
    CATEGORIES_CACHE_TTL_SECONDS: int = 300
    PRODUCTS_CACHE_TTL_SECONDS: int = 120
    ANALYTICS_CACHE_TTL_SECONDS: int = 60
    USER_SESSION_CACHE_TTL_SECONDS: int = 1800 

    SECONDS_IN_MINUTE: int = 60

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self) -> str:
        return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Глобальный экземпляр настроек
settings = Settings()
