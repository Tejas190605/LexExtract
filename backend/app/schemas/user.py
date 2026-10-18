from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str
    role: str = "USER"
    is_active: bool = True


class UserRegister(BaseModel):
    """
    User registration payload.
    Strictly forces new public registrations to role USER.
    Enforces minimum 8-character password.
    """
    email: str
    username: str
    full_name: str
    password: str = Field(..., min_length=8, description="Minimum 8 characters")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        clean = v.strip().lower()
        if len(clean) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if not clean.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, hyphens, and underscores.")
        return clean

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return clean


UserCreate = UserRegister


class UserLogin(BaseModel):
    """
    JSON credentials login payload (allows email or username).
    """
    email_or_username: str
    password: str


class TokenResponse(BaseModel):
    """
    OAuth2-compatible Bearer JWT token response.
    Never exposes passwords, hashes, or sensitive profile secrets.
    """
    access_token: str
    token_type: str = "bearer"
    user: Optional["UserResponse"] = None


class UserResponse(BaseModel):
    """
    Public response schema for User entity.
    STRICT SECURITY RULE: password_hash is NEVER exposed in API responses.
    """
    id: int
    username: str
    email: str
    full_name: str
    name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in ["USER", "ANALYST", "ADMIN"]:
            raise ValueError("Role must be one of: USER, ANALYST, ADMIN.")
        return clean
