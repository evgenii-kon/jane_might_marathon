import secrets
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "GET":
            token = secrets.token_urlsafe(32)
            request.state.csrf_token = token
            response = await call_next(request)
            response.set_cookie(
                key="csrftoken",
                value=token,
                httponly=False,
                samesite="lax",
                secure=False,
                max_age=3600,
            )
            return response

        if request.method == "POST":
            cookie_token = request.cookies.get("csrftoken")

            # Читаем тело один раз и кешируем его в _body,
            # тогда повторный вызов request.form() в роуте
            # прочитает из кеша, а не из уже закрытого стрима
            body = await request.body()
            request._body = body  # ← вот главная строчка

            form_data = await request.form()
            form_token = form_data.get("csrf_token")
            if not form_token:
                form_token = request.headers.get("X-CSRFToken")

            if not cookie_token or not form_token or cookie_token != form_token:
                raise HTTPException(
                    status_code=403, detail="CSRF token verification failed"
                )

        return await call_next(request)


def get_csrf_token(request: Request) -> str:
    return getattr(request.state, "csrf_token", request.cookies.get("csrftoken", ""))