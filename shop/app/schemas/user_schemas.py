from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    is_active: bool
    role_id: int
    role_name: str | None = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
    full_name: str
    is_active: bool = True
    role: int
    last_login: datetime | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password_hash: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    role: int | None = None
    last_login: datetime | None = None


class UserOut(UserBase):
    id: int
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserDB(UserOut):
    password_hash: str




