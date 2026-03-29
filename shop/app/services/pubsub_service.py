import asyncio
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Awaitable

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class PubSubChannel(str, Enum):
    CACHE_INVALIDATION = "ch:cache_invalidation"
    SESSION_INVALIDATION = "ch:session_invalidation"
    DATA_CHANGE = "ch:data_change"


class PubSubService:
    def __init__(self, instance_id: str):
        self._instance_id = instance_id
        self._redis: Redis | None = None
        self._pubsub = None
        self._handlers: dict[str, list[Callable[[dict], Awaitable[None]]]] = {}
        self._running = False
        self._listener_task: asyncio.Task | None = None

    @property
    def instance_id(self) -> str:
        return self._instance_id

    @property
    def is_running(self) -> bool:
        return self._running

    async def connect(self, redis_client: Redis) -> None:
        self._redis = redis_client
        self._pubsub = self._redis.pubsub()

    def on(
        self,
        channel: PubSubChannel,
        handler: Callable[[dict], Awaitable[None]],
    ) -> None:
        self._handlers.setdefault(channel.value, []).append(handler)

    async def subscribe_all(self) -> None:
        if not self._pubsub:
            raise RuntimeError("PubSubService not connected")
        channels = list(self._handlers.keys())
        if channels:
            await self._pubsub.subscribe(*channels)

    async def publish(
        self,
        channel: PubSubChannel,
        event: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        if not self._redis:
            return
        message = {
            "event": event,
            "instance_id": self._instance_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(data or {}),
        }
        await self._redis.publish(channel.value, json.dumps(message))

    async def start_listener(self) -> None:
        if not self._pubsub:
            raise RuntimeError("PubSubService not connected")
        self._running = True
        logger.info(
            "PubSub listener started on instance %s, channels: %s",
            self._instance_id,
            list(self._handlers.keys()),
        )
        try:
            while self._running:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0,
                )
                if message is None:
                    await asyncio.sleep(0.05)
                    continue
                await self._dispatch(message)
        except asyncio.CancelledError:
            logger.info("PubSub listener cancelled on instance %s", self._instance_id)
        except Exception:
            logger.exception("PubSub listener error on instance %s", self._instance_id)
        finally:
            self._running = False

    async def _dispatch(self, raw_message: dict) -> None:
        channel = raw_message.get("channel", "")
        data_str = raw_message.get("data")
        if not isinstance(data_str, str):
            return

        try:
            payload: dict = json.loads(data_str)
        except (json.JSONDecodeError, TypeError):
            return

        if payload.get("instance_id") == self._instance_id:
            return

        handlers = self._handlers.get(channel, [])
        for handler in handlers:
            try:
                await handler(payload)
            except Exception:
                logger.exception(
                    "Handler error on channel %s, instance %s",
                    channel,
                    self._instance_id,
                )

    async def stop(self) -> None:
        self._running = False
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.aclose()
            self._pubsub = None
