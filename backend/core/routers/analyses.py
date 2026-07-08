"""Code analysis routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import User, Analysis, Issue, Project
from ..schemas import AnalysisRead, IssueRead
from ..security import get_current_user
from ..modules.analyzer import create_analyzer

router = APIRouter(prefix="/analyses", tags=["analyses"])

@router.post("/analyze")
async def analyze_code(
    project_id: str,
    file_path: str,
    code: str,
    language: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze code
    
    Args:
        project_id: Project ID
        file_path: File path
        code: Code content
        language: Programming language
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Analysis result
        
    Raises:
        HTTPException: If project not found or unauthorized
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
    
    try:
        # Perform analysis
        analyzer = create_analyzer(code, language)
        issues = analyzer.analyze()
        
        # Create analysis record
        analysis = Analysis(
            project_id=project_id,
            file_path=file_path,
            language=language,
            total_issues=len(issues),
            quality_score=100 - (len(issues) * 5),  # Simple scoring
            metadata={"analyzer": "my-agent-v1"}
        )
        
        db.add(analysis)
        await db.flush()
        
        # Add issues
        for issue in issues:
            db_issue = Issue(
                analysis_id=analysis.id,
                line_number=issue.line,
                column_number=issue.column,
                severity=issue.severity,
                rule_id="syntax-error",
                message=issue.message,
            )
            db.add(db_issue)
        
        await db.commit()
        await db.refresh(analysis)
        
        return {
            "analysis_id": str(analysis.id),
            "file_path": file_path,
            "language": language,
            "total_issues": analysis.total_issues,
            "quality_score": analysis.quality_score,
            "issues": [issue.to_dict() for issue in issues],
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/project/{project_id}", response_model=List[AnalysisRead])
async def get_project_analyses(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project analyses
    
    Args:
        project_id: Project ID
        skip: Skip count
        limit: Limit count
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of analyses
        
    Raises:
        HTTPException: If project not found or unauthorized
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
    
    result = await db.execute(
        select(Analysis)
        .where(Analysis.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    analyses = result.scalars().all()
    
    return analyses

@router.get("/{analysis_id}", response_model=AnalysisRead)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get analysis by ID
    
    Args:
        analysis_id: Analysis ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Analysis information
        
    Raises:
        HTTPException: If analysis not found or unauthorized
    """
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalars().first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Verify project ownership
    project = await db.get(Project, analysis.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this analysis"
        )
    
    return analysis

@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete analysis
    
    Args:
        analysis_id: Analysis ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If analysis not found or unauthorized
    """
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalars().first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Verify project ownership
    project = await db.get(Project, analysis.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this analysis"
        )
    
    await db.delete(analysis)
    await db.commit()
