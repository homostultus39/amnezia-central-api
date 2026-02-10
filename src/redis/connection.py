import redis.asyncio as redis

from src.management.settings import get_settings


settings = get_settings()

redis_client = None


async def connect_redis():
    global redis_client
    redis_client = await redis.from_url(
        f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
        encoding="utf8",
        decode_responses=True
    )
    return redis_client


async def disconnect_redis():
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis():
    return redis_client
