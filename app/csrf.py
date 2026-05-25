import secrets
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


CSRF_SESSION_KEY = "csrf_token"


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерируем токен один раз и храним в сессии навсегда
        if CSRF_SESSION_KEY not in request.session:
            request.session[CSRF_SESSION_KEY] = secrets.token_urlsafe(32)

        if request.method == "POST":
            session_token = request.session.get(CSRF_SESSION_KEY)

            body = await request.body()
            request._body = body
            form_data = await request.form()
            form_token = form_data.get("csrf_token")

            print(f"SESSION TOKEN: {session_token}")
            print(f"FORM TOKEN: {form_token}")

            if not form_token:
                form_token = request.headers.get("X-CSRFToken")

            if not session_token or not form_token or session_token != form_token:
                raise HTTPException(
                    status_code=403, detail="CSRF token verification failed"
                )

        return await call_next(request)


def get_csrf_token(request: Request) -> str:
    return request.session.get(CSRF_SESSION_KEY, "")