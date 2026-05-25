from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .routes.admin.dashboard import router as admin_router
from .routes.dashboard.dashboard import router as dashboard_router
from .routes.admin.lesson import router as lesson_router
from .routes.admin.week import router as week_router
from .routes.admin.word import router as word_router
from .routes.admin.exercise import router as exercise_admin_router
from .routes.dashboard.exercises import router as exercise_router
from app.routes.admin.article import router as article_admin_router
from .routes.public.public import router as public_router
from .routes.auth import router as auth_router
from .routes.admin.user import router as admin_user_router
from .routes.dashboard.weeks import router as dashboard_weeks_router
from .routes.dashboard.lessons import router as dashboard_lessons_router
from .routes.dashboard.word_trainer.word_trainer import router as word_trainer_router
from .routes.dashboard.word_trainer.word_trainer_modes import router as word_trainer_modes_router
from .routes.public.articles import router as article_router
from app.routes.dashboard.feedback import router as feedback_router
from .routes.admin.feedback import router as admin_feedback_router

from .csrf import CSRFMiddleware, get_csrf_token
from app.utils.rate_limiter import limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .config import settings

from .database import init_db, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_middleware(CSRFMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(admin_router)
app.include_router(dashboard_router)
app.include_router(dashboard_weeks_router)
app.include_router(dashboard_lessons_router)
app.include_router(public_router)
app.include_router(lesson_router)
app.include_router(week_router)
app.include_router(word_router)
app.include_router(auth_router)
app.include_router(admin_user_router)
app.include_router(exercise_admin_router)
app.include_router(exercise_router)
app.include_router(word_trainer_modes_router)
app.include_router(article_admin_router)
app.include_router(article_router)
app.include_router(word_trainer_router)
app.include_router(feedback_router)
app.include_router(admin_feedback_router)

templates = Jinja2Templates("app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates.env.globals["csrf"] = get_csrf_token


@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})