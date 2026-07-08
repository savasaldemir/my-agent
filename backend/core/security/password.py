"""Password hashing utilities"""

from passlib.context import CryptContext
from passlib.exc import InvalidTokenError

# Configure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except InvalidTokenError:
        return False
