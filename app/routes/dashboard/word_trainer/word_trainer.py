from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.subscription import require_feature
from app.models.user import User
from app.repositories.user_word_mistake_repository import UserWordMistakeRepository

router = APIRouter(prefix="/word-trainer", tags=["word_trainer"])


@router.get("/", response_class=HTMLResponse)
async def word_trainer_hub(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("word_trainer")),
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
