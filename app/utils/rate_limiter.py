from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func = get_remote_address,
    storage_uri='memory://',
    strategy='fixed-window',
    headers_enabled=True
)

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Too many requests. Limit: {exc.limit}. Retry after {exc.retry_after} seconds."}
    )