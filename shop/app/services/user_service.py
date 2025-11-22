from fastapi import HTTPException, status

from shop.app.repositories.user_repository import UserRepository
from shop.app.schemas.user_schemas import (
    UserCreate,
    UserOut,
    UserUpdate,
)
from shop.app.core.security import hash_password


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, user_id: int) -> UserOut:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def list_users(self, limit: int, offset: int) -> list[UserOut]:
        return await self.user_repo.get_all(limit=limit, offset=offset)

    async def create_user(self, payload: UserCreate) -> UserOut:
        if await self.user_repo.exists_with_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        if await self.user_repo.exists_with_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        user_data = payload.model_dump()

        # Hash password before saving
        user_data["password_hash"] = hash_password(payload.password_hash)

        user_id = await self.user_repo.create(user_data)
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to fetch created user",
            )
        return user

    async def update_user(self, user_id: int, payload: UserUpdate) -> UserOut:
        # Ensure user exists
        await self.get_user_by_id(user_id)

        update_data = payload.model_dump(exclude_unset=True)

        if "password_hash" in update_data and update_data["password_hash"]:
            update_data["password_hash"] = hash_password(update_data["password_hash"])

        updated = await self.user_repo.update(user_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to fetch updated user",
            )
        return user

    async def delete_user(self, user_id: int) -> None:
        # Ensure user exists
        await self.get_user_by_id(user_id)

        deleted = await self.user_repo.delete(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            )


