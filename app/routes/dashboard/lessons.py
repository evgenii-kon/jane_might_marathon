from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.subscription import require_feature_or_trial_lesson
from app.models.user import User

from app.services.lesson_service import LessonService
from app.services.word_trainer_service import WordTrainerService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.services.user_week_progress_service import UserWeekProgressService
from app.services.word_service import WordService
from app.services.user_activity_service import UserActivityService
from app.services.novel_service import NovelService
from app.services.user_novel_progress_service import UserNovelProgressService
from app.csrf import get_csrf_token


router = APIRouter(prefix="/dashboard/lessons", tags=["dashboard"])



@router.get("/{lesson_id}", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def lesson_detail(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature_or_trial_lesson("lessons")),
):
    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)
    word_service = WordService(db)
    word_trainer_service = WordTrainerService(db)
    novel_service = NovelService(db)
    novel_progress_service = UserNovelProgressService(db)

    lesson = await lesson_service.get_lesson_by_id(lesson_id)

    await progress_service.mark_lesson_as_started(current_user.id, lesson_id)

    # mark_lesson_as_started гарантирует is_started=True, повторный запрос не нужен
    is_started = True
    is_completed = await progress_service.is_lesson_completed(current_user.id, lesson_id)

    words = await word_service.get_words_by_lesson(lesson_id)
    await word_trainer_service.add_lesson_words_to_progress(current_user.id, lesson_id)

    novel_lines = await novel_service.get_lines_by_lesson(lesson_id)
    novel_already_seen = await novel_progress_service.has_seen(current_user.id, lesson_id)

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
            "novel_lines": [line.model_dump(mode="json") for line in novel_lines],
            "novel_skipped": current_user.novel_skipped,
            "novel_already_seen": novel_already_seen,
            "user_name": current_user.name,
        },
    )


@router.post("/{lesson_id}/mark-novel-seen")
async def mark_novel_seen(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Отметить, что пользователь досмотрел/пропустил новеллу этого урока —
    чтобы при следующем заходе в урок она не показывалась автоматически снова"""
    novel_progress_service = UserNovelProgressService(db)
    await novel_progress_service.mark_seen(current_user.id, lesson_id)
    return {"ok": True}


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature_or_trial_lesson("lessons")),
):
    """Отметить урок как пройденный"""
    progress_service = UserLessonProgressService(db)
    lesson_service = LessonService(db)
    week_progress_service = UserWeekProgressService(db)

    # Получаем урок, чтобы узнать week_id
    lesson = await lesson_service.get_lesson_by_id(lesson_id)

    # Отмечаем урок пройденным
    await progress_service.mark_lesson_as_completed(current_user.id, lesson_id)

    activity_service = UserActivityService(db)
    await activity_service.record_activity(current_user.id)

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