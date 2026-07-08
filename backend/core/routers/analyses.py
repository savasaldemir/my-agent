"""Code analysis routes"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from ..database import get_db
from ..models import User, Analysis, Issue, Project
from ..schemas import AnalysisRead, IssueRead
from ..security import get_current_user
from ..modules.analyzer_factory import create_analyzer, get_supported_languages

router = APIRouter(prefix="/analyses", tags=["analyses"])

@router.get("/supported-languages")
async def get_supported_langs():
    """Get supported programming languages"""
    return {
        "languages": get_supported_languages(),
        "count": len(get_supported_languages()),
    }

@router.post("/analyze")
async def analyze_code(
    project_id: str,
    file_path: str,
    code: str,
    language: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze code with advanced analysis engine
    
    Args:
        project_id: Project ID
        file_path: File path
        code: Code content
        language: Programming language
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Analysis result with detailed metrics and issues
        
    Raises:
        HTTPException: If project not found or analysis fails
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
        # Create appropriate analyzer
        analyzer = create_analyzer(code, language)
        
        # Run analysis
        issues = analyzer.analyze()
        
        # Calculate metrics
        metrics = analyzer.calculate_metrics()
        
        # Create analysis record
        analysis = Analysis(
            project_id=project_id,
            file_path=file_path,
            language=language,
            total_issues=len(issues),
            quality_score=int(metrics.quality_score),
            security_score=int(metrics.security_score),
            performance_score=int(metrics.complexity_score),
            metadata={
                "analyzer_version": "1.0.0-alpha",
                "metrics": {
                    "total_lines": metrics.total_lines,
                    "code_lines": metrics.code_lines,
                    "comment_lines": metrics.comment_lines,
                    "blank_lines": metrics.blank_lines,
                    "complexity_score": metrics.complexity_score,
                    "maintainability_score": metrics.maintainability_score,
                    "average_score": metrics.average_score(),
                }
            }
        )
        
        db.add(analysis)
        await db.flush()
        
        # Add issues to database
        for issue in issues:
            db_issue = Issue(
                analysis_id=analysis.id,
                line_number=issue.line,
                column_number=issue.column,
                severity=issue.severity,
                rule_id=issue.rule,
                message=issue.message,
                suggestion=issue.suggestion,
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
            "security_score": analysis.security_score,
            "performance_score": analysis.performance_score,
            "metrics": analysis.metadata.get("metrics", {}),
            "issues": [issue.to_dict() for issue in issues],
            "severity_breakdown": {
                "critical": len([i for i in issues if i.severity.value == "critical"]),
                "error": len([i for i in issues if i.severity.value == "error"]),
                "warning": len([i for i in issues if i.severity.value == "warning"]),
                "info": len([i for i in issues if i.severity.value == "info"]),
            },
            "category_breakdown": {
                "syntax": len([i for i in issues if i.category.value == "syntax"]),
                "style": len([i for i in issues if i.category.value == "style"]),
                "performance": len([i for i in issues if i.category.value == "performance"]),
                "security": len([i for i in issues if i.category.value == "security"]),
                "maintainability": len([i for i in issues if i.category.value == "maintainability"]),
                "complexity": len([i for i in issues if i.category.value == "complexity"]),
            },
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
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
        .order_by(Analysis.created_at.desc())
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
