import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator


# --- User ---


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # from_attributes=True allows Pydantic to read data from SQLAlchemy model instances
    model_config = {"from_attributes": True}


# --- Auth ---


# AuthResponse returns both token and user data so the client doesn't need
# a separate request to get user info after login/register
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


# --- Message ---


class MessageCreate(BaseModel):
    text: str = Field(min_length=1, max_length=4096)
    receiver_id: uuid.UUID


class MessageResponse(BaseModel):
    id: int
    text: str
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Pagination ---


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


# --- HC ---


class HealthResponse(BaseModel):
    status: str
    db: str
