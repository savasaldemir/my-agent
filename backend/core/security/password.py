"""Password hashing utilities"""

import hashlib
import hmac
import secrets

_ITERATIONS = 120_000


def _derive_key(password: str, salt: str) -> str:
    """Derive a stable hash for password verification."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS)
    return dk.hex()

def get_password_hash(password: str) -> str:
    """Hash password using PBKDF2-SHA256
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    salt = secrets.token_hex(16)
    digest = _derive_key(password, salt)
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${digest}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        algorithm, rounds, salt, digest = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        computed = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            int(rounds),
        ).hex()
        return hmac.compare_digest(computed, digest)
    except (ValueError, TypeError):
        return False
