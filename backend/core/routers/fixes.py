"""Code fix routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db
from ..models import User, Project
from ..security import get_current_user
from ..modules.fix_factory import create_fixer, create_suggester
from sqlalchemy import select

router = APIRouter(prefix="/fixes", tags=["fixes"])

class FixRequest(BaseModel):
    """Fix request"""
    project_id: str
    file_path: str
    code: str
    language: str
    auto_fix: bool = False

class ApplyFixRequest(BaseModel):
    """Apply fix request"""
    code: str
    language: str
    rule: str
    fix_all: bool = False

@router.post("/suggest")
async def suggest_fixes(
    request: FixRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get fix suggestions for code
    
    Args:
        request: Fix request with code and language
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of fix suggestions
        
    Raises:
        HTTPException: If project not found or suggestion generation fails
    """
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            (Project.id == request.project_id) &
            (Project.user_id == current_user.id)
        )
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        suggester = create_suggester(request.code, request.language)
        suggestions = suggester.generate_suggestions()
        
        return {
            "file_path": request.file_path,
            "language": request.language,
            "total_suggestions": len(suggestions),
            "suggestions": [s.to_dict() for s in suggestions],
            "automatic_count": len([s for s in suggestions if s.fix_level.value == "automatic"]),
            "safe_count": len([s for s in suggestions if s.fix_level.value == "safe"]),
            "risky_count": len([s for s in suggestions if s.fix_level.value == "risky"]),
            "manual_count": len([s for s in suggestions if s.fix_level.value == "manual"]),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}"
        )

@router.post("/apply")
async def apply_fixes(
    request: ApplyFixRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply fixes to code
    
    Args:
        request: Apply fix request
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Fixed code
    """
    try:
        fixer = create_fixer(request.code, request.language)
        
        if request.fix_all:
            fixed_code = fixer.auto_fix()
        else:
            fixed_code = fixer.auto_fix_rule(request.rule)
        
        return {
            "original_code": request.code,
            "fixed_code": fixed_code,
            "language": request.language,
            "rule": request.rule,
            "changes": len(request.code.split('\n')) - len(fixed_code.split('\n')),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply fixes: {str(e)}"
        )

@router.post("/preview")
async def preview_fix(
    request: ApplyFixRequest,
    current_user: User = Depends(get_current_user),
):
    """Preview a fix without applying it
    
    Args:
        request: Apply fix request
        current_user: Current authenticated user
        
    Returns:
        Diff preview
    """
    try:
        fixer = create_fixer(request.code, request.language)
        fixed_code = fixer.auto_fix_rule(request.rule)
        
        original_lines = request.code.split('\n')
        fixed_lines = fixed_code.split('\n')
        
        diff = []
        for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines), 1):
            if orig != fixed:
                diff.append({
                    "line": i,
                    "original": orig,
                    "fixed": fixed,
                })
        
        return {
            "rule": request.rule,
            "language": request.language,
            "changes": len(diff),
            "diff": diff,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
