"""
CSRF защита для FastAPI + Jinja2
"""

import secrets
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware для проверки CSRF токена"""

    async def dispatch(self, request: Request, call_next):
        # Для GET запросов — устанавливаем токен в cookies
        if request.method == "GET":
            response = await call_next(request)
            token = secrets.token_urlsafe(32)
            response.set_cookie(
                key="csrftoken",  # ← единое имя
                value=token,
                httponly=False,  # ← Должен быть False, чтобы JS мог читать
                samesite="lax",
                secure=False,
                max_age=3600,
            )
            return response

        # Для POST запросов — проверяем токен
        if request.method == "POST":
            # Получаем токен из cookies
            cookie_token = request.cookies.get("csrftoken")  # ← единое имя

            # Получаем токен из формы
            form = await request.form()
            form_token = form.get("csrf_token")

            # Также проверяем заголовок (для AJAX)
            if not form_token:
                form_token = request.headers.get("X-CSRFToken")

            if not cookie_token or not form_token or cookie_token != form_token:
                raise HTTPException(
                    status_code=403, detail="CSRF token verification failed"
                )

        return await call_next(request)


def csrf_context_processor(request: Request) -> dict:
    """Контекстный процессор — передаёт токен в шаблон"""
    token = request.cookies.get("csrftoken", "")  # ← единое имя
    return {
        "csrf_input": f'<input type="hidden" name="csrf_token" value="{token}">',
        "csrf_token": token,
    }
