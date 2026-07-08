"""User model"""

from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
        })
        return data
