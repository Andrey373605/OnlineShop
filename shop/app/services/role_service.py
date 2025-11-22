from fastapi import HTTPException

from shop.app.repositories.role_repository import RoleRepository
from shop.app.schemas.role_schemas import (
    RoleCreate,
    RoleOut,
    RoleResponse,
    RoleUpdate,
)


class RoleService:
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    async def create_role(self, data: RoleCreate) -> RoleResponse:
        if await self.role_repo.exists_with_name(data.name):
            raise HTTPException(status_code=400, detail="Role name already exists")

        role_id = await self.role_repo.create(data.name)
        if not role_id:
            raise HTTPException(status_code=500, detail="Failed to create role")

        return RoleResponse(id=role_id, message="Role created successfully")

    async def get_role_by_id(self, role_id: int) -> RoleOut:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    async def get_all_roles(self) -> list[RoleOut]:
        return await self.role_repo.get_all()

    async def update_role(self, role_id: int, data: RoleUpdate) -> RoleResponse:
        await self.get_role_by_id(role_id)

        # В текущей схеме RoleUpdate не делает поля опциональными,
        # поэтому просто используем переданное имя.
        if await self.role_repo.exists_with_name(data.name):
            raise HTTPException(status_code=400, detail="Role name already exists")

        success = await self.role_repo.update(role_id, data.name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update role")

        return RoleResponse(id=role_id, message="Role updated successfully")

    async def delete_role(self, role_id: int) -> RoleResponse:
        await self.get_role_by_id(role_id)

        success = await self.role_repo.delete(role_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete role")

        return RoleResponse(id=role_id, message="Role deleted successfully")



