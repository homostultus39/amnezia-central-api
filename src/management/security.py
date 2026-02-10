import bcrypt
from datetime import datetime, timedelta, timezone
import jwt

from src.management.settings import get_settings


settings = get_settings()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(subject: str) -> str:
    """Create access token."""
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    """Create refresh token."""
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(minutes=settings.jwt_refresh_token_expire_minutes)
    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode JWT token."""
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def get_token_ttl(token: str) -> int:
    """
    Calculate remaining TTL (in seconds) until token expires.

    Args:
        token: JWT token

    Returns:
        Remaining seconds until expiration (minimum 1 second)
    """
    payload = decode_token(token)
    exp_timestamp = payload.get("exp", 0)
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    ttl = exp_timestamp - now_timestamp
    return max(ttl, 1)
