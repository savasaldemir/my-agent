"""Code analysis endpoints"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..modules.analyzer import create_analyzer

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    """Code analysis request"""

    code: str
    language: str
    features: List[str] = ["quality", "security", "performance"]


class IssueItem(BaseModel):
    """Code issue"""

    line: int
    column: int
    severity: str  # info, warning, error
    message: str
    rule: str


class AnalysisResponse(BaseModel):
    """Analysis response"""

    issues: List[IssueItem]
    metrics: dict
    suggestions: List[str]


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: AnalysisRequest):
    """Analyze code for issues and metrics"""
    try:
        analyzer = create_analyzer(request.code, request.language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    issues = [IssueItem(**issue.to_dict()) for issue in analyzer.analyze()]
    lines = request.code.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    metrics = {
        "lines": len(lines),
        "non_empty_lines": len(non_empty_lines),
        "issues_count": len(issues),
    }

    suggestions: List[str] = []
    if any(item.severity in ["error", "critical"] for item in issues):
        suggestions.append("Fix syntax and critical issues before proceeding.")
    if "security" in request.features:
        suggestions.append("Review secrets and unsafe eval/exec usage.")
    if "performance" in request.features:
        suggestions.append("Profile hotspots before applying optimizations.")

    return AnalysisResponse(
        issues=issues,
        metrics=metrics,
        suggestions=suggestions,
    )


@router.post("/upload")
async def upload_for_analysis(file: UploadFile = File(...)):
    """Upload file for analysis"""
    if file.size and file.size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=413, detail="File too large")

    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Only UTF-8 text files are supported")

    filename = file.filename or "uploaded"
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    language_map = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
    }
    language = language_map.get(extension, "python")

    result = await analyze_code(
        AnalysisRequest(
            code=text,
            language=language,
            features=["quality", "security", "performance"],
        )
    )

    return {
        "message": "File analyzed",
        "filename": filename,
        "analysis": result.model_dump(),
    }
