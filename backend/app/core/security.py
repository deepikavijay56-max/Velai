import random
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: str,
    role: str,
    college_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token."""
    jwt_secret = _get_jwt_secret()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "college_id": college_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """Generate a signed refresh token."""
    jwt_secret = _get_jwt_secret()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(to_encode, jwt_secret, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except (jwt.PyJWTError, RuntimeError):
        return None


def _get_jwt_secret() -> str:
    if not settings.JWT_SECRET:
        raise RuntimeError("JWT_SECRET must be configured before using JWT authentication")
    return settings.JWT_SECRET


def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP or return fixed OTP in mock mode."""
    if settings.DEV_MODE and settings.DEV_OTP_CODE:
        return settings.DEV_OTP_CODE
    return "".join(random.choices(string.digits, k=length))


def validate_college_email(email: str, required_domain: Optional[str] = None) -> bool:
    """Verify that an email belongs to the configured campus domain."""
    domain = (required_domain or settings.COLLEGE_EMAIL_DOMAIN).lower().strip()
    clean_email = email.lower().strip()
    return clean_email.endswith(f"@{domain}") or clean_email.endswith(f".{domain}")
