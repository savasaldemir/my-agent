"""Authentication service"""

from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..schemas import UserCreate, UserLogin
from ..security.jwt import create_access_token, create_refresh_token, verify_token
from .user_service import UserService
import jwt


class AuthService:
    """Authentication business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    async def register(self, user_data: UserCreate) -> Tuple[User, str, str]:
        """Register new user
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            ValueError: If registration fails
        """
        try:
            user = await self.user_service.create_user(user_data)
            await self.db.commit()

            access_token = create_access_token(str(user.id))
            refresh_token = create_refresh_token(str(user.id))

            return user, access_token, refresh_token
        except ValueError as e:
            await self.db.rollback()
            raise e
    
    async def login(self, login_data: UserLogin) -> Tuple[User, str, str]:
        """Login user
        
        Args:
            login_data: Login credentials
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            ValueError: If login fails
        """
        user = await self.user_service.authenticate_user(
            login_data.username,
            login_data.password,
        )
        
        if not user:
            raise ValueError("Invalid username or password")
        
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        return user, access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token
            
        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            user_id = verify_token(refresh_token, "refresh")
            access_token = create_access_token(user_id)
            return access_token
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
