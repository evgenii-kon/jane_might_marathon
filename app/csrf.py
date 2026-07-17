import secrets
import hmac
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


CSRF_SESSION_KEY = "csrf_token"


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерируем токен если его нет
        if CSRF_SESSION_KEY not in request.session:
            request.session[CSRF_SESSION_KEY] = secrets.token_urlsafe(32)

        # Пропускаем webhook Tinkoff без CSRF
        if request.method == "POST" and request.url.path == "/payment/webhook":
            return await call_next(request)

        if request.method == "POST":
            session_token = request.session.get(CSRF_SESSION_KEY)

            body = await request.body()
            request._body = body
            form_data = await request.form()
            form_token = form_data.get("csrf_token")

            if not form_token:
                form_token = request.headers.get("X-CSRFToken")

            if not session_token or not form_token or not hmac.compare_digest(
                session_token, str(form_token)
            ):
                raise HTTPException(
                    status_code=403, detail="CSRF token verification failed"
                )

            # Ротировать токен после каждого успешного POST
            request.session[CSRF_SESSION_KEY] = secrets.token_urlsafe(32)

        return await call_next(request)


def get_csrf_token(request: Request) -> str:
    return request.session.get(CSRF_SESSION_KEY, "")