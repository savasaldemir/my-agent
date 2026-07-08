"""Authentication schemas"""

from pydantic import BaseModel
from typing import Optional, Dict, Any

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None

class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str
    exp: int
    iat: int
    type: str
