from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/word-trainer", tags=["word_trainer"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def word_trainer_hub(request: Request, current_user: User = Depends(get_current_user)):
    """
    Страница выбора режима тренажёра
    """
    return templates.TemplateResponse(
        "word_trainer/hub.html", {"request": request, "user": current_user}
    )
