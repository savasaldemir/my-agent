"""Project schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str
    language: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    repository_provider: Optional[str] = None

class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass

class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None

class ProjectRead(ProjectBase):
    """Project read schema"""
    id: str
    user_id: str
    default_branch: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
