from src.management.settings import get_settings
from src.redis.connection import get_redis
from src.management.security import get_token_ttl


settings = get_settings()


async def add_token_to_blacklist(token: str) -> None:
    """Add JWT token to blacklist."""
    redis = await get_redis()
    ttl = get_token_ttl(token)
    await redis.setex(f"blacklist:{token}", ttl, "1")


async def is_token_blacklisted(token: str) -> bool:
    """Check if JWT token is in blacklist."""
    redis = await get_redis()
    result = await redis.exists(f"blacklist:{token}")
    return bool(result)


async def remove_token_from_blacklist(token: str) -> None:
    """Remove JWT token from blacklist."""
    redis = await get_redis()
    await redis.delete(f"blacklist:{token}")
