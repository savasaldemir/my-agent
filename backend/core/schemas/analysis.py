"""Analysis schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class IssueRead(BaseModel):
    """Issue read schema"""
    id: str
    line_number: int
    column_number: Optional[int]
    severity: str
    rule_id: str
    message: str
    suggestion: Optional[str]
    fixed: bool
    
    class Config:
        from_attributes = True

class AnalysisRead(BaseModel):
    """Analysis read schema"""
    id: str
    project_id: str
    file_path: str
    language: str
    total_issues: int
    quality_score: Optional[int]
    security_score: Optional[int]
    performance_score: Optional[int]
    issues: List[IssueRead] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
