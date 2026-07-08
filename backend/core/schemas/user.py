"""User schemas"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema"""
    password: str

class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserRead(UserBase):
    """User read schema"""
    id: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str
