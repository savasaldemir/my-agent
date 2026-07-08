"""Analysis session model"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid

class Session(BaseModel):
    """Analysis session"""
    
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    session_type = Column(String(50), nullable=False)  # analyze, fix, test, optimize
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    total_issues = Column(Integer, default=0)
    fixed_issues = Column(Integer, default=0)
    duration_seconds = Column(Integer)
    metadata = Column(JSON)
    
    # Relationships
    project = relationship("Project", backref="sessions")
    user = relationship("User", backref="sessions")
    
    __table_args__ = (
        Index('idx_session_project_id', 'project_id'),
        Index('idx_session_user_id', 'user_id'),
        Index('idx_session_status', 'status'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'project_id': str(self.project_id),
            'user_id': str(self.user_id),
            'session_type': self.session_type,
            'status': self.status,
            'total_issues': self.total_issues,
            'fixed_issues': self.fixed_issues,
            'duration_seconds': self.duration_seconds,
        })
        return data
