from pydantic import BaseModel, Field, EmailStr  # noqa: F401 – EmailStr kept for future input validation
from typing import Optional, Literal


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    totp_code: Optional[str] = None


class UserIdentity(BaseModel):
    id: str
    username: str
    role: Literal["case_client", "admin_builder"]
    displayName: str
    # Plain str here: seed accounts use .local domains that EmailStr rejects.
    # Switch to EmailStr when production email domains are required.
    email: Optional[str] = None


class SessionPayload(BaseModel):
    token: str
    expiresAt: str


class LoginResponse(BaseModel):
    user: UserIdentity
    session: SessionPayload


class MeResponse(BaseModel):
    id: str
    username: str
    role: Literal["case_client", "admin_builder"]
    displayName: str
    capabilities: dict
