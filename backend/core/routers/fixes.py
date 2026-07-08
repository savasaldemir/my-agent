"""Fix Suggestion Router"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from ..services.fix_service import FixSuggestionEngine

router = APIRouter(
    prefix="/fixes",
    tags=["fixes"]
)

class FixRequest(BaseModel):
    project_id: Optional[str] = None
    file_path: Optional[str] = "main.py"
    code: str
    language: str
    auto_fix: Optional[bool] = False

class QuickFixApplyRequest(BaseModel):
    code: str
    language: str
    rule: str

@router.post("/suggest", status_code=status.HTTP_200_OK)
async def get_fix_suggestions(payload: FixRequest):
    """Kod girdisini analiz eder ve yapay zeka/AST tabanlı düzeltme önerileri hazırlar."""
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Analiz edilecek kod boş olamaz.")
    
    result = FixSuggestionEngine.analyze_and_suggest(
        code=payload.code,
        language=payload.language,
        auto_fix=payload.auto_fix
    )
    return result

@router.post("/apply", status_code=status.HTTP_200_OK)
async def apply_specific_fix(payload: QuickFixApplyRequest):
    """Belirli bir kurala göre koddaki hatayı anında tamir eder."""
    result = FixSuggestionEngine.analyze_and_suggest(
        code=payload.code,
        language=payload.language,
        auto_fix=True
    )
    return {
        "rule_applied": payload.rule,
        "fixed_code": result["fixed_code"]
    }
