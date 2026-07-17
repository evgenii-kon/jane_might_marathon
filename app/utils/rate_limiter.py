from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    strategy='fixed-window',
    headers_enabled=True
)

templates = Jinja2Templates(directory="app/templates")

# Маппинг маршрутов на шаблоны для HTML-ответов
_ROUTE_TEMPLATES: dict[str, str] = {
    "/auth/login": "auth/login.html",
    "/auth/register": "auth/register.html",
}


async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    # exc.detail содержит строку вида "5 per 1 minute"
    error_msg = "Слишком много попыток. Пожалуйста, подождите немного и попробуйте снова."

    template_name = _ROUTE_TEMPLATES.get(request.url.path)

    if template_name:
        from app.csrf import get_csrf_token
        response = templates.TemplateResponse(
            template_name,
            {
                "request": request,
                "error": error_msg,
                "csrf_token": get_csrf_token(request),
            },
            status_code=429,
        )
    else:
        response = JSONResponse(
            status_code=429,
            content={"detail": error_msg},
        )

    # Добавляем Retry-After и X-RateLimit-* заголовки через slowapi
    view_rate_limit = getattr(request.state, "view_rate_limit", None)
    if view_rate_limit is not None:
        response = request.app.state.limiter._inject_headers(response, view_rate_limit)

    return response
