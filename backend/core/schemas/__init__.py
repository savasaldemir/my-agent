"""Pydantic schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration payload."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login payload."""

    username: str
    password: str


class UserUpdate(BaseModel):
    """User update payload."""

    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    """User response payload."""

    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
