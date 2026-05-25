from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.services.lesson_service import LessonService
from app.services.word_trainer_service import WordTrainerService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.services.user_week_progress_service import UserWeekProgressService
from app.services.word_service import WordService
from app.csrf import get_csrf_token 


router = APIRouter(prefix="/dashboard/lessons", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")



@router.get("/{lesson_id}", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def lesson_detail(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)
    word_service = WordService(db)
    word_trainer_service = WordTrainerService(db)

    lesson = await lesson_service.get_lesson_by_id(lesson_id)

    await progress_service.mark_lesson_as_started(current_user.id, lesson_id)

    is_started = await progress_service.is_lesson_started(current_user.id, lesson_id)
    is_completed = await progress_service.is_lesson_completed(current_user.id, lesson_id)

    words = await word_service.get_words_by_lesson(lesson_id)
    await word_trainer_service.add_lesson_words_to_progress(current_user.id, lesson_id)

    return templates.TemplateResponse(
        "dashboard/lessons/lesson_detail.html",
        {
            "request": request,
            "lesson": lesson,
            "is_started": is_started,
            "is_completed": is_completed,
            "words": words,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Отметить урок как пройденный"""
    progress_service = UserLessonProgressService(db)
    lesson_service = LessonService(db)
    week_progress_service = UserWeekProgressService(db)

    # Получаем урок, чтобы узнать week_id
    lesson = await lesson_service.get_lesson_by_id(lesson_id)

    # Отмечаем урок пройденным
    await progress_service.mark_lesson_as_completed(current_user.id, lesson_id)

    # Получаем все уроки недели и количество пройденных — двумя запросами вместо N
    lessons_in_week = await lesson_service.get_lessons_by_week(lesson.week_id)
    completed_count = await progress_service.get_completed_count_by_week(
        current_user.id, lesson.week_id
    )

    # Если все уроки недели пройдены, отмечаем неделю как пройденную
    if completed_count == len(lessons_in_week):
        await week_progress_service.mark_week_completed(current_user.id, lesson.week_id)

    # Редирект обратно на страницу недели
    return RedirectResponse(url=f"/dashboard/weeks/{lesson.week_id}", status_code=302)