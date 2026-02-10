from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
import jwt

from src.management.settings import get_settings
from src.management.security import decode_token
from src.api.v1.deps.exceptions.auth import InvalidTokenException, TokenNotProvidedException
from src.redis.client import RedisClient

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Get current admin from Bearer token."""
    if not credentials:
        raise TokenNotProvidedException()

    token = credentials.credentials
    redis_client = RedisClient()

    # Check if token is blacklisted
    if await redis_client.is_token_blacklisted(token):
        raise InvalidTokenException()

    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenException()
        return username
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
