from pydantic import BaseModel, EmailStr


class AuthUserOut(BaseModel):
    """Minimal user info for auth responses (register/login)."""
    id: int
    username: str
    email: EmailStr
    full_name: str
    role_id: int
    role_name: str | None = None


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str


class RegisterResponse(BaseModel):
    """Response for registration — no tokens, user must log in."""
    message: str = "Registration successful"
    user: AuthUserOut


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
    user: AuthUserOut
    tokens: TokenPair


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(TokenPair):
    pass


class LogoutRequest(BaseModel):
    refresh_token: str




