import bcrypt
from datetime import datetime, timezone
import jwt

from src.management.settings import get_settings


settings = get_settings()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def get_token_ttl(token: str) -> int:
    """
    Calculate remaining TTL (in seconds) until token expires.

    Args:
        token: JWT token

    Returns:
        Remaining seconds until expiration (minimum 1 second)
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    exp_timestamp = payload.get("exp", 0)
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    ttl = exp_timestamp - now_timestamp
    return max(ttl, 1)
