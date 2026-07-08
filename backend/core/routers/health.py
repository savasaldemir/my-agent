"""Health check endpoints"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0-alpha",
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready"}
