from fastapi import HTTPException, status

from shop.app.schemas.user_schemas import UserOut


def is_admin(user: UserOut) -> bool:
    if user is None:
        return False
    is_admin_name = (user.role_name or "").lower() == "admin"
    is_admin_id = user.role_id == 1
    return is_admin_name or is_admin_id


def _ensure_admin(current_user: UserOut) -> None:
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )