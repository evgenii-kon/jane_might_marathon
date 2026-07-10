from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.feedback import FeedbackCreate
from app.services.feedback_service import FeedbackService
from app.csrf import get_csrf_token 


router = APIRouter(prefix="/dashboard/feedback", tags=["dashboard_feedback"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def feedback_form(
    request: Request,
    sent: bool = False,
    current_user: User = Depends(get_current_user),
):
    """Отображает форму обратной связи"""
    return templates.TemplateResponse(
        "dashboard/feedback_form.html",
        {
            "request": request,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
            "success": "Спасибо! Ваш отзыв отправлен." if sent else None,
            }
    )


@router.post("/", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    text: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обрабатывает отправку формы"""
    service = FeedbackService(db)
    await service.create_feedback(current_user.id, FeedbackCreate(text=text))
    return RedirectResponse(url="/dashboard/feedback/?sent=true", status_code=302)