from dataclasses import dataclass

from shop.app.core.config import Settings


@dataclass(frozen=True)
class CacheServiceConfig:
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str | None
    block_time_minutes: int
    seconds_in_minute: int

    @classmethod
    def from_settings(cls, settings: Settings) -> "CacheServiceConfig":
        return cls(
            redis_host=settings.REDIS_HOST,
            redis_port=settings.REDIS_PORT,
            redis_db=settings.REDIS_DB,
            redis_password=settings.REDIS_PASSWORD,
            block_time_minutes=settings.BLOCK_TIME_MINUTES,
            seconds_in_minute=settings.SECONDS_IN_MINUTE,
        )
