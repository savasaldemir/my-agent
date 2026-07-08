"""Project management routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import User, Project
from ..schemas import ProjectRead, ProjectCreate, ProjectUpdate
from ..security import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectRead])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's projects
    
    Args:
        skip: Skip count
        limit: Limit count
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of projects
    """
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    return projects

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new project
    
    Args:
        project_data: Project data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created project
    """
    project = Project(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        language=project_data.language,
        repository_url=project_data.repository_url,
        repository_provider=project_data.repository_provider,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project by ID
    
    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Project information
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) &
            (Project.user_id == current_user.id)
        )
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project
    
    Args:
        project_id: Project ID
        project_data: Update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated project
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) &
            (Project.user_id == current_user.id)
        )
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project
    
    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If project not found or unauthorized
    """
    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) &
            (Project.user_id == current_user.id)
        )
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()
