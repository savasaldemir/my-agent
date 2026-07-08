"""Analysis and Issue models"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid
import enum

class IssueSeverity(str, enum.Enum):
    """Issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Analysis(BaseModel):
    """Code analysis result"""
    
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    language = Column(String(50), nullable=False)
    total_issues = Column(Integer, default=0)
    quality_score = Column(Integer)  # 0-100
    security_score = Column(Integer)
    performance_score = Column(Integer)
    metadata = Column(JSON)  # Additional analysis data
    
    # Relationships
    project = relationship("Project", backref="analyses")
    issues = relationship("Issue", backref="analysis", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_analysis_project_id', 'project_id'),
        Index('idx_analysis_file_path', 'file_path'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'project_id': str(self.project_id),
            'file_path': self.file_path,
            'language': self.language,
            'total_issues': self.total_issues,
            'quality_score': self.quality_score,
            'security_score': self.security_score,
            'performance_score': self.performance_score,
        })
        return data

class Issue(BaseModel):
    """Code issue from analysis"""
    
    __tablename__ = "issues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'), nullable=False)
    line_number = Column(Integer, nullable=False)
    column_number = Column(Integer)
    severity = Column(Enum(IssueSeverity), nullable=False)
    rule_id = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    suggestion = Column(Text)
    fixed = Column(String(1), default='0')
    
    __table_args__ = (
        Index('idx_issue_analysis_id', 'analysis_id'),
        Index('idx_issue_severity', 'severity'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'analysis_id': str(self.analysis_id),
            'line_number': self.line_number,
            'column_number': self.column_number,
            'severity': self.severity.value,
            'rule_id': self.rule_id,
            'message': self.message,
            'suggestion': self.suggestion,
            'fixed': self.fixed == '1',
        })
        return data
