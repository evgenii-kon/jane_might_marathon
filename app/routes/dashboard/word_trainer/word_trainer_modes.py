import random
from fastapi import Form, APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.word_trainer_service import WordTrainerService
from app.services.user_activity_service import UserActivityService
from app.repositories.word_repository import WordRepository
from app.repositories.user_word_progress_repository import UserWordProgressRepository
from app.repositories.user_word_mistake_repository import UserWordMistakeRepository
from app.csrf import get_csrf_token
import re

router = APIRouter(prefix="/word-trainer", tags=["word_trainer"])


@router.get("/daily", response_class=HTMLResponse)
async def daily_trainer(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Режим ежедневного повторения"""
    service = WordTrainerService(db)
    words_progress = await service.get_daily_session(current_user.id)

    random.shuffle(words_progress)
    words = []
    for wp in words_progress:
        word = wp.word
        words.append({
            "id": word.id,
            "word": word.hanzi,
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
    raw_words = await service.get_all_words_session(current_user.id)
    words = [
        {
            "id": w.id,
            "word": w.hanzi,
            "translation": w.translation,
            "transcription": w.transcription,
            "example_sentence": w.example_sentence,
            "audio_url": w.audio_url,
            "mastery_level": None,
        }
        for w in raw_words
    ]

    return templates.TemplateResponse(
        "word_trainer/session.html",
        {
            "request": request,
            "words": words,
            "mode": "all",
            "mode_name": "Все слова",
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/matching", response_class=HTMLResponse)
async def matching_trainer(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Режим сопоставления пар"""
    service = WordTrainerService(db)
    raw_words = await service.get_all_words_session(current_user.id)
    words = [
        {"id": w.id, "word": w.hanzi, "translation": w.translation}
        for w in raw_words
    ]
    return templates.TemplateResponse(
        "word_trainer/matching.html",
        {"request": request, "words": words, "user": current_user, "mode_name": "Сопоставление пар"},
    )


@router.get("/mistakes", response_class=HTMLResponse)
async def mistakes_trainer(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Режим работы над ошибками"""
    mistake_repo = UserWordMistakeRepository(db)
    mistake_words = await mistake_repo.get_mistakes(current_user.id)

    words = [
        {
            "id": w.id,
            "word": w.hanzi,
            "translation": w.translation,
            "transcription": w.transcription,
            "example_sentence": w.example_sentence,
            "audio_url": w.audio_url,
            "mastery_level": None,
        }
        for w in mistake_words
    ]
    random.shuffle(words)

    return templates.TemplateResponse(
        "word_trainer/session.html",
        {
            "request": request,
            "words": words,
            "mode": "mistakes",
            "mode_name": "Мои ошибки",
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
    mistake_repo = UserWordMistakeRepository(db)

    word = await word_repo.get_by_id(word_id)
    if not word:
        return {"error": "Word not found"}

    cleaned = re.sub(r'\(.*?\)', '', word.translation)
    parts = {p.strip().lower() for p in re.split(r'[/,]', cleaned) if p.strip()}

    is_correct = user_answer.lower().strip() in parts

    progress = await service.progress_repo.update_mastery(
        current_user.id, word_id, is_correct
    )

    if not is_correct:
        # Ошибка в любом режиме → слово в стек
        await mistake_repo.add_mistake(current_user.id, word_id)
    elif mode == "mistakes":
        # Правильный ответ В РЕЖИМЕ ОШИБОК → убрать из стека
        await mistake_repo.remove_mistake(current_user.id, word_id)
    # Правильный ответ в daily/all → НЕ убирать из стека (только режим ошибок убирает)

    if mode == "daily" and is_correct:
        activity_service = UserActivityService(db)
        await activity_service.record_activity(current_user.id)

    return {
        "is_correct": is_correct,
        "translation": word.translation,
        "transcription": word.transcription,
        "example": word.example_sentence,
        "new_mastery_level": progress.mastery_level,
        "next_review_days": UserWordProgressRepository.MASTERY_INTERVALS.get(
            progress.mastery_level, 1
        ),
        "mistake_stack_count": await mistake_repo.get_mistake_count(current_user.id),
    }