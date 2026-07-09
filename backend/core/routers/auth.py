"""Authentication routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import UserCreate, UserLogin, UserRead
from ..schemas.auth import TokenResponse
from ..services import AuthService
from ..security.permission import get_current_user
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    """Refresh token payload"""

    refresh_token: str

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register new user
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Access token, refresh token, and user info
    """
    try:
        auth_service = AuthService(db)
        user, access_token, refresh_token = await auth_service.register(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login user
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Access token, refresh token, and user info
    """
    try:
        auth_service = AuthService(db)
        user, access_token, refresh_token = await auth_service.login(login_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token
    
    Args:
        refresh_token: Refresh token
        db: Database session
        
    Returns:
        New access token
    """
    try:
        auth_service = AuthService(db)
        access_token = await auth_service.refresh_access_token(payload.refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": payload.refresh_token,
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get current user info
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user.to_dict()

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """Logout user
    
    Note: Logout is handled client-side by removing the token
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
