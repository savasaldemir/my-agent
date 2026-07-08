"""JWT token utilities"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import jwt
from ..config import settings

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create JWT access token
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        additional_claims: Additional claims to include
        
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=int(settings.jwt_expiration_hours))
    
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )
    
    return encoded_jwt

def create_refresh_token(subject: str) -> str:
    """Create JWT refresh token
    
    Args:
        subject: Token subject (usually user ID)
        
    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=7)
    
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify token and return subject
    
    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)
        
    Returns:
        Subject (user ID) if token is valid
        
    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    payload = decode_token(token)
    
    if payload.get("type") != token_type:
        raise jwt.InvalidTokenError(f"Expected {token_type} token")
    
    subject = payload.get("sub")
    if not subject:
        raise jwt.InvalidTokenError("Token has no subject")
    
    return subject
