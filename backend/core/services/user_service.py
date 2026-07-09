"""User service"""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..schemas import UserCreate, UserUpdate
from ..security.password import get_password_hash, verify_password


class UserService:
    """User business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If username or email already exists
        """
        existing = await self.db.execute(
            select(User).where((User.username == user_data.username) | (User.email == user_data.email))
        )
        if existing.scalars().first():
            raise ValueError("Username or email already exists")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )

        self.db.add(user)
        await self.db.flush()

        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username
        
        Args:
            username: Username
            
        Returns:
            User or None
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email
        
        Args:
            email: Email address
            
        Returns:
            User or None
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_user_by_username(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def update_user(
        self,
        user_id: str,
        user_data: UserUpdate,
    ) -> Optional[User]:
        """Update user
        
        Args:
            user_id: User ID
            user_data: Update data
            
        Returns:
            Updated user or None
        """
        user = await self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        
        return user
