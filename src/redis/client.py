from src.redis.connection import get_redis


class RedisClient:
    """Redis client for token blacklist management."""

    async def blacklist_token(self, token: str, ex: int) -> None:
        """Add JWT token to blacklist with TTL."""
        redis = await get_redis()
        await redis.setex(f"blacklist:{token}", ex, "1")

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if JWT token is in blacklist."""
        redis = await get_redis()
        result = await redis.exists(f"blacklist:{token}")
        return bool(result)

    async def remove_token_from_blacklist(self, token: str) -> None:
        """Remove JWT token from blacklist."""
        redis = await get_redis()
        await redis.delete(f"blacklist:{token}")
