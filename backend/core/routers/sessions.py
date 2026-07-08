"""Session management routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import User, Session, Project
from ..security import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/", response_model=List[dict])
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's sessions
    
    Args:
        skip: Skip count
        limit: Limit count
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of sessions
    """
    result = await db.execute(
        select(Session)
        .where(Session.user_id == current_user.id)
        .order_by(Session.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()
    return [session.to_dict() for session in sessions]

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_session(
    project_id: str,
    session_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new session
    
    Args:
        project_id: Project ID
        session_type: Session type (analyze, fix, test, optimize)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created session
        
    Raises:
        HTTPException: If project not found or invalid session type
    """
    # Verify project ownership
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
    
    if session_type not in ["analyze", "fix", "test", "optimize"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session type"
        )
    
    session = Session(
        project_id=project_id,
        user_id=current_user.id,
        session_type=session_type,
        status="pending",
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session.to_dict()

@router.get("/{session_id}", response_model=dict)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get session by ID
    
    Args:
        session_id: Session ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Session information
        
    Raises:
        HTTPException: If session not found or unauthorized
    """
    result = await db.execute(
        select(Session).where(
            (Session.id == session_id) &
            (Session.user_id == current_user.id)
        )
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session.to_dict()

@router.put("/{session_id}", response_model=dict)
async def update_session(
    session_id: str,
    status: str,
    total_issues: int = None,
    fixed_issues: int = None,
    duration_seconds: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update session
    
    Args:
        session_id: Session ID
        status: Session status (running, completed, failed)
        total_issues: Total issues found
        fixed_issues: Issues fixed
        duration_seconds: Session duration
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated session
        
    Raises:
        HTTPException: If session not found or unauthorized
    """
    result = await db.execute(
        select(Session).where(
            (Session.id == session_id) &
            (Session.user_id == current_user.id)
        )
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = status
    if total_issues is not None:
        session.total_issues = total_issues
    if fixed_issues is not None:
        session.fixed_issues = fixed_issues
    if duration_seconds is not None:
        session.duration_seconds = duration_seconds
    
    await db.commit()
    await db.refresh(session)
    
    return session.to_dict()

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete session
    
    Args:
        session_id: Session ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If session not found or unauthorized
    """
    result = await db.execute(
        select(Session).where(
            (Session.id == session_id) &
            (Session.user_id == current_user.id)
        )
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    await db.delete(session)
    await db.commit()
