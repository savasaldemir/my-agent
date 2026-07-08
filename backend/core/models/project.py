"""Project model"""

from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .base import BaseModel
import uuid

class Project(BaseModel):
    """Project model"""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    language = Column(String(50), nullable=False)
    repository_url = Column(String(500))
    repository_provider = Column(String(50))  # github, gitlab, bitbucket
    default_branch = Column(String(100), default='main')
    is_public = Column(String(1), default='0')
    
    # Relationships
    user = relationship("User", backref="projects")
    
    __table_args__ = (
        Index('idx_project_user_id', 'user_id'),
        Index('idx_project_language', 'language'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'user_id': str(self.user_id),
            'name': self.name,
            'description': self.description,
            'language': self.language,
            'repository_url': self.repository_url,
            'repository_provider': self.repository_provider,
            'default_branch': self.default_branch,
        })
        return data
