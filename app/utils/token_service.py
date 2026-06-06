import secrets
from app.redis_client import get_redis


VERIFY_EMAIL_TTL = 86400
RESET_PASSWORD_TTL = 900


async def create_verification_token ( user_id: int) -> str:
    redis = get_redis()
    token = secrets.token_urlsafe(32)
    await redis.setex(f'verify_email:{token}', VERIFY_EMAIL_TTL, str(user_id))
    return token


async def verify_email_token(token: str) -> int | None:
    redis = get_redis()
    user_id = await redis.get(f'verify_email:{token}')
    if not user_id:
        return None
    await redis.delete(f"verify_email:{token}")
    return int(user_id)


async def create_reset_password_token(user_id: int) -> str:
    redis = get_redis()
    token = secrets.token_urlsafe(32)
    await redis.setex(f"reset_password:{token}", RESET_PASSWORD_TTL, str(user_id))
    return token


async def verify_reset_password_token(token: str) -> int | None:
    redis = get_redis()
    user_id = await redis.get(f"reset_password:{token}")
    if not user_id:
        return None
    await redis.delete(f"reset_password:{token}")
    return int(user_id)

