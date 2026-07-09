"""Project management endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Project

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    """Create project request"""

    name: str
    description: Optional[str] = None
    language: str
    repository_url: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response"""

    id: str
    name: str
    description: Optional[str]
    language: str
    repository_url: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project"""
    project_model = Project(
        name=project.name,
        description=project.description,
        language=project.language,
        repository_url=project.repository_url,
    )
    db.add(project_model)
    await db.commit()
    await db.refresh(project_model)
    return ProjectResponse(**project_model.to_dict())


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects"""
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return [ProjectResponse(**project.to_dict()) for project in result.scalars().all()]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get project details"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project.to_dict())


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()
