from pydantic import BaseModel, EmailStr

from shop.app.schemas.user_schemas import UserOut


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenPair(BaseModel):
    token_type: str = "bearer"
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int


class AuthResponse(BaseModel):
    user: UserOut
    tokens: TokenPair


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(TokenPair):
    pass


class LogoutRequest(BaseModel):
    refresh_token: str




