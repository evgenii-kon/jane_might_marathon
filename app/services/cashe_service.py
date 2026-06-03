import json
from app.redis_client import get_redis

class CacheService:
    def __init__(self, prefix: str, ttl: int = 300):
        self.prefix = prefix
        self.ttl = ttl  # секунды

    def _key(self, *parts) -> str:
        return f"{self.prefix}:" + ":".join(str(p) for p in parts)

    async def get(self, *key_parts):
        redis = get_redis()
        data = await redis.get(self._key(*key_parts))
        if data is not None:
            return json.loads(data)
        return None

    async def set(self, value, *key_parts) -> None:
        redis = get_redis()
        await redis.setex(self._key(*key_parts), self.ttl, json.dumps(value))

    async def delete(self, *key_parts) -> None:
        redis = get_redis()
        await redis.delete(self._key(*key_parts))

    async def delete_pattern(self, pattern: str) -> None:
        """Удалить все ключи по паттерну, напр. 'lessons:*'"""
        redis = get_redis()
        keys = await redis.keys(f"{self.prefix}:{pattern}")
        if keys:
            await redis.delete(*keys)