import hashlib
from datetime import date, datetime, time, timedelta
from typing import Optional

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.word_repository import WordRepository
from app.schemas.word import WordResponse

WORD_OF_DAY_KEY = "word_of_day"


def _seconds_until_midnight() -> int:
    now = datetime.now()
    midnight = datetime.combine(now.date() + timedelta(days=1), time.min)
    return int((midnight - now).total_seconds())


async def get_word_of_day(db: AsyncSession, redis: aioredis.Redis) -> Optional[WordResponse]:
    cached = await redis.get(WORD_OF_DAY_KEY)
    if cached:
        return WordResponse.model_validate_json(cached)

    repository = WordRepository(db)
    all_ids = await repository.get_all_ids()
    if not all_ids:
        return None

    today = date.today().isoformat()
    hash_int = int(hashlib.md5(today.encode()).hexdigest(), 16)
    word_id = all_ids[hash_int % len(all_ids)]

    word = await repository.get_by_id(word_id)
    result = WordResponse.model_validate(word)

    await redis.setex(WORD_OF_DAY_KEY, _seconds_until_midnight(), result.model_dump_json())
    return result
