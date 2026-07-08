"""Base model with common fields"""

from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields"""
    
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
