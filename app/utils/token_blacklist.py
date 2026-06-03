from ..services.cashe_service import get_redis
from ..config import settings


async def blacklist_token(token: str) -> None:
    redis = get_redis()
    ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis.setex(f'blacklist:{token}', ttl, '1')


async def is_token_in_blacklist(token: str) -> bool:
    redis = get_redis()
    return await redis.exists(f'blacklist:{token}') == 1