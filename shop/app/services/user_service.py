from shop.app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.core.security import hash_password
from shop.app.models.schemas import (
    UserCreate,
    UserOut,
    UserUpdate,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.cache_service import CacheService
from shop.app.services.pubsub_service import PubSubChannel, PubSubService
from shop.app.services.session_service import SessionService


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        pubsub: PubSubService,
        session_service: SessionService,
        cache_ttl_seconds: int | None = None,
    ):
        self._uow = uow
        self._cache = cache
        self._pubsub = pubsub
        self._session_service = session_service
        self._cache_ttl_seconds = cache_ttl_seconds
        self._cache_pattern = "users:limit:*"

    async def get_user_by_id(self, user_id: int) -> UserOut:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User")
            return user

    async def list_users(self, limit: int, offset: int) -> list[UserOut]:
        key = f"users:limit:{limit}:offset:{offset}"

        if await self._cache.exists(key):
            users_str = await self._cache.get_list(key)
            return [UserOut.model_validate_json(s) for s in users_str]

        async with self._uow as uow:
            users = await uow.users.get_all(limit=limit, offset=offset)

        users_str = [u.model_dump_json() for u in users]
        await self._cache.set_list_atomic(
            key, users_str, ttl_seconds=self._cache_ttl_seconds
        )
        return users

    async def create_user(self, payload: UserCreate) -> UserOut:
        async with self._uow as uow:
            if await uow.users.exists_with_username(payload.username):
                raise AlreadyExistsError("Username")

            if await uow.users.exists_with_email(payload.email):
                raise AlreadyExistsError("Email")

            user_data = payload.model_dump(exclude={"password"})
            user_data["password_hash"] = hash_password(payload.password)

            user_id = await uow.users.create(user_data)
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise OperationFailedError("Unable to fetch created user")
            await uow.commit()

        await self._cache.delete_by_pattern(self._cache_pattern)
        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "users", "pattern": self._cache_pattern},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "users", "action": "create", "entity_id": user.id},
        )
        return user

    async def update_user(self, user_id: int, payload: UserUpdate) -> UserOut:
        async with self._uow as uow:
            existing = await uow.users.get_by_id(user_id)
            if not existing:
                raise NotFoundError("User")

            update_data = payload.model_dump(exclude_unset=True)

            if "password" in update_data and update_data["password"]:
                update_data["password_hash"] = hash_password(update_data["password"])
                del update_data["password"]

            updated = await uow.users.update(user_id, update_data)
            if not updated:
                raise OperationFailedError("Failed to update user")

            user = await uow.users.get_by_id(user_id)
            if not user:
                raise OperationFailedError("Unable to fetch updated user")
            await uow.commit()

        await self._cache.delete_by_pattern(self._cache_pattern)
        await self._session_service.delete_all_user_sessions(user_id)

        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "users", "pattern": self._cache_pattern},
        )
        await self._pubsub.publish(
            PubSubChannel.SESSION_INVALIDATION,
            event="session_invalidated",
            data={"user_id": user_id},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "users", "action": "update", "entity_id": user_id},
        )
        return user

    async def delete_user(self, user_id: int) -> None:
        async with self._uow as uow:
            existing = await uow.users.get_by_id(user_id)
            if not existing:
                raise NotFoundError("User")

            deleted = await uow.users.delete(user_id)
            if not deleted:
                raise OperationFailedError("Failed to delete user")
            await uow.commit()

        await self._cache.delete_by_pattern(self._cache_pattern)
        await self._session_service.delete_all_user_sessions(user_id)

        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "users", "pattern": self._cache_pattern},
        )
        await self._pubsub.publish(
            PubSubChannel.SESSION_INVALIDATION,
            event="session_invalidated",
            data={"user_id": user_id},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "users", "action": "delete", "entity_id": user_id},
        )
