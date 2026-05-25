from fastapi import Form, APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.word_trainer_service import WordTrainerService
from app.repositories.word_repository import WordRepository
from ....schemas.word import WordResponse
from app.csrf import get_csrf_token

router = APIRouter(prefix="/word-trainer", tags=["word_trainer"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/daily", response_class=HTMLResponse)
async def daily_trainer(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Режим ежедневного повторения"""
    service = WordTrainerService(db)
    words_progress = await service.get_daily_session(current_user.id)

    words = []
    for wp in words_progress:
        # Если у слова есть атрибут `word` (связь), то используем его, иначе wp.word — это объект Word
        word = wp.word
        words.append({
            "id": word.id,
            "word": word.hanzi or word.word,
            "translation": word.translation,
            "transcription": word.transcription,
            "example_sentence": word.example_sentence,
            "audio_url": word.audio_url,
            "mastery_level": wp.mastery_level,
        })

    due_count = await service.get_due_count(current_user.id)

    return templates.TemplateResponse(
        "word_trainer/session.html",
        {
            "request": request,
            "words": words,
            "due_count": due_count,
            "mode": "daily",
            "mode_name": "Ежедневное повторение",
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/all", response_class=HTMLResponse)
async def all_words_trainer(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Режим всех слов (без учёта повторений)"""
    service = WordTrainerService(db)
    words = await service.get_all_words_session(current_user.id)
    words_schemas = [WordResponse.model_validate(word) for word in words]
    words_dicts = [word.model_dump() for word in words_schemas]

    return templates.TemplateResponse(
        "word_trainer/session.html",
        {
            "request": request,
            "words": words_dicts,
            "mode": "all",
            "mode_name": "Все слова",
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/check")
async def check_answer(
    word_id: int = Form(...),
    user_answer: str = Form(...),
    mode: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Проверка ответа пользователя"""
    word_repo = WordRepository(db)
    service = WordTrainerService(db)

    word = await word_repo.get_by_id(word_id)
    if not word:
        return {"error": "Word not found"}

    is_correct = user_answer.lower().strip() == word.translation.lower().strip()

    if mode == "daily":
        # Обновляем прогресс только для ежедневного режима
        progress = await service.progress_repo.update_mastery(
            current_user.id, word_id, is_correct
        )
        intervals = {0: 1, 1: 3, 2: 7, 3: 14, 4: 30, 5: 60}

        return {
            "is_correct": is_correct,
            "translation": word.translation,
            "transcription": word.transcription,
            "example": word.example_sentence,
            "new_mastery_level": progress.mastery_level,
            "next_review_days": intervals.get(progress.mastery_level, 1),
        }
    else:
        # Для режима 'all' просто возвращаем результат
        return {
            "is_correct": is_correct,
            "translation": word.translation,
            "transcription": word.transcription,
            "example": word.example_sentence,
            "new_mastery_level": None,
            "next_review_days": None,
        }