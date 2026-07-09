from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.user_word_mistake_repository import UserWordMistakeRepository

router = APIRouter(prefix="/word-trainer", tags=["word_trainer"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def word_trainer_hub(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Страница выбора режима тренажёра
    """
    mistake_repo = UserWordMistakeRepository(db)
    mistake_count = await mistake_repo.get_mistake_count(current_user.id)

    return templates.TemplateResponse(
        "word_trainer/hub.html",
        {"request": request, "user": current_user, "mistake_count": mistake_count},
    )
