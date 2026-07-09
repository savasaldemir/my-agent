"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel
from . import UserRead


class TokenResponse(BaseModel):
    """Auth token response."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserRead] = None
