from shop.app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.models.schemas import (
    RoleCreate,
    RoleOut,
    RoleResponse,
    RoleUpdate,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.cache_service import CacheService
from shop.app.services.pubsub_service import PubSubChannel, PubSubService

ROLES_CACHE_KEY = "roles:all"


class RoleService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        pubsub: PubSubService,
        cache_ttl_seconds: int | None = None,
    ):
        self._uow = uow
        self._cache = cache
        self._pubsub = pubsub
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_role(self, data: RoleCreate) -> RoleResponse:
        async with self._uow as uow:
            if await uow.roles.exists_with_name(data.name):
                raise AlreadyExistsError("Role name")

            role_id = await uow.roles.create(data.name)
            if not role_id:
                raise OperationFailedError("Failed to create role")
            await uow.commit()

        await self._invalidate_roles_cache()
        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "roles", "key": ROLES_CACHE_KEY},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "roles", "action": "create", "entity_id": role_id},
        )
        return RoleResponse(id=role_id, message="Role created successfully")

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        async with self._uow as uow:
            role = await uow.roles.get_by_id(role_id)
            if not role:
                raise NotFoundError("Role")
            return role

    async def get_all_roles(self) -> list[RoleOut]:
        if await self._cache.exists(ROLES_CACHE_KEY):
            roles_str = await self._cache.get_list(ROLES_CACHE_KEY)
            return [RoleOut.model_validate_json(s) for s in roles_str]

        async with self._uow as uow:
            roles = await uow.roles.get_all()

        roles_str = [r.model_dump_json() for r in roles]
        await self._cache.set_list_atomic(
            ROLES_CACHE_KEY, roles_str, ttl_seconds=self._cache_ttl_seconds
        )
        return roles

    async def update_role(self, role_id: int, data: RoleUpdate) -> RoleResponse:
        async with self._uow as uow:
            role = await uow.roles.get_by_id(role_id)
            if not role:
                raise NotFoundError("Role")

            if await uow.roles.exists_with_name(data.name):
                raise AlreadyExistsError("Role name")

            success = await uow.roles.update(role_id, data.name)
            if not success:
                raise OperationFailedError("Failed to update role")
            await uow.commit()

        await self._invalidate_roles_cache()
        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "roles", "key": ROLES_CACHE_KEY},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "roles", "action": "update", "entity_id": role_id},
        )
        return RoleResponse(id=role_id, message="Role updated successfully")

    async def delete_role(self, role_id: int) -> RoleResponse:
        async with self._uow as uow:
            role = await uow.roles.get_by_id(role_id)
            if not role:
                raise NotFoundError("Role")

            success = await uow.roles.delete(role_id)
            if not success:
                raise OperationFailedError("Failed to delete role")
            await uow.commit()

        await self._invalidate_roles_cache()
        await self._pubsub.publish(
            PubSubChannel.CACHE_INVALIDATION,
            event="cache_invalidated",
            data={"entity": "roles", "key": ROLES_CACHE_KEY},
        )
        await self._pubsub.publish(
            PubSubChannel.DATA_CHANGE,
            event="data_changed",
            data={"entity": "roles", "action": "delete", "entity_id": role_id},
        )
        return RoleResponse(id=role_id, message="Role deleted successfully")

    async def _invalidate_roles_cache(self) -> None:
        await self._cache.delete(ROLES_CACHE_KEY)
