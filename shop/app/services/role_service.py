from fastapi import HTTPException

from shop.app.repositories.role_repository import RoleRepository
from shop.app.schemas.role_schemas import (
    RoleCreate,
    RoleOut,
    RoleResponse,
    RoleUpdate,
)
from shop.app.services.cache_service import CacheService

ROLES_CACHE_KEY = "roles:all"


class RoleService:
    def __init__(
        self,
        role_repo: RoleRepository,
        cache: CacheService,
        cache_ttl_seconds: int | None = None,
    ):
        self.role_repo = role_repo
        self.cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    async def create_role(self, data: RoleCreate) -> RoleResponse:
        if await self.role_repo.exists_with_name(data.name):
            raise HTTPException(status_code=400, detail="Role name already exists")

        role_id = await self.role_repo.create(data.name)
        if not role_id:
            raise HTTPException(status_code=500, detail="Failed to create role")

        await self._invalidate_roles_cache()
        return RoleResponse(id=role_id, message="Role created successfully")

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    async def get_all_roles(self) -> list[RoleOut]:
        if await self.cache.exists(ROLES_CACHE_KEY):
            roles_str = await self.cache.get_list(ROLES_CACHE_KEY)
            return [RoleOut.model_validate_json(s) for s in roles_str]

        roles = await self.role_repo.get_all()
        roles_str = [r.model_dump_json() for r in roles]
        await self.cache.set_list_atomic(
            ROLES_CACHE_KEY, roles_str, ttl_seconds=self._cache_ttl_seconds
        )
        return roles

    async def update_role(self, role_id: int, data: RoleUpdate) -> RoleResponse:
        await self.get_role_by_id(role_id)

        if await self.role_repo.exists_with_name(data.name):
            raise HTTPException(status_code=400, detail="Role name already exists")

        success = await self.role_repo.update(role_id, data.name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update role")

        await self._invalidate_roles_cache()
        return RoleResponse(id=role_id, message="Role updated successfully")

    async def delete_role(self, role_id: int) -> RoleResponse:
        await self.get_role_by_id(role_id)

        success = await self.role_repo.delete(role_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete role")

        await self._invalidate_roles_cache()
        return RoleResponse(id=role_id, message="Role deleted successfully")

    async def _invalidate_roles_cache(self) -> None:
        await self.cache.delete(ROLES_CACHE_KEY)
