import redis.asyncio as aioredis
from .config import settings

redis_client: aioredis.Redis | None = None

async def init_redis() -> None:
    global redis_client
    redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await redis_client.ping()

async def close_redis() -> None:
    if redis_client:
        await redis_client.aclose()

def get_redis() -> aioredis.Redis:
    return redis_client