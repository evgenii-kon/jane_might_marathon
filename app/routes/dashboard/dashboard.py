from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.services.word_trainer_service import WordTrainerService
from app.services.user_week_progress_service import UserWeekProgressService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Сервисы
    week_service = WeekService(db)
    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)
    word_trainer_service = WordTrainerService(db)
    week_progress_service = UserWeekProgressService(db)

    # Данные пользователя
    user = current_user
    # Используем UTC-дату для корректного вычисления независимо от серверной timezone
    today_utc = datetime.now(timezone.utc).date()
    created_date = user.created_at.date() if user.created_at.tzinfo else user.created_at.replace(tzinfo=timezone.utc).date()
    days_after_start = (today_utc - created_date).days

    # Все недели
    weeks = await week_service.get_all_weeks()

    # Общий прогресс по урокам
    total_lessons = await lesson_service.get_lessons_count()
    completed_lessons = await progress_service.get_completed_count_by_user(user.id)
    progress_percent = (
        int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    )

    # Прогресс по неделям
    weeks_with_progress = []
    now = datetime.now(timezone.utc)

    for week in weeks:
        week_progress = await progress_service.get_week_progress(current_user.id, week.id)

        # Получаем opens_at для этой недели
        user_week_progress = await week_progress_service.repository.get_by_user_and_week(
            current_user.id, week.id
        )

        if user_week_progress:
            opens_at = user_week_progress.opens_at
            if opens_at.tzinfo is None:
                opens_at = opens_at.replace(tzinfo=timezone.utc)
            is_locked = now < opens_at
            days_until_open = (opens_at - now).days + 1 if is_locked else None
        else:
            # Если нет записи — неделя 1 открыта, остальные по расписанию
            if week.number == 1:
                is_locked = False
                # Для первой недели можно создать запись, чтобы избежать повторных проверок
                await week_progress_service.get_or_create(current_user.id, week.id)
            else:
                # Создаём запись для первой недели, если нет
                await week_progress_service.get_or_create(current_user.id, week.id)
                is_locked = True
            days_until_open = None

        weeks_with_progress.append({
            "id": week.id,
            "number": week.number,
            "short_description": week.short_description,
            "total_lessons": week_progress.total_lessons,
            "completed_lessons": week_progress.completed_lessons,
            "progress_percent": week_progress.progress_percent,
            "is_locked": is_locked,
            "is_completed": week_progress.is_week_completed,
            "days_until_open": days_until_open,
        })

    # Статистика по словам
    due_today = await word_trainer_service.get_due_count(user.id)
    mastery_stats = await word_trainer_service.get_mastery_stats(user.id)
    mastered_words = mastery_stats.get(5, 0)
    learned_words = sum(v for k, v in mastery_stats.items() if k >= 3)
    total_words = await word_trainer_service.get_total_words_count(current_user.id)

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "user": current_user,
            "days_after_start": days_after_start,
            "weeks": weeks_with_progress,
            "total_completed": completed_lessons,
            "total_lessons": total_lessons,
            "progress_percent": progress_percent,
            "due_today": due_today,
            "mastered_words": mastered_words,
            "learned_words": learned_words,
            "total_words": total_words,
        },
    )


@router.get('/words/rating', response_class=HTMLResponse)
async def word_rating(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = WordTrainerService(db)
    words = await service.get_word_ranking(current_user.id)

    cnt_mastered = sum(1 for w in words if w['mastery_level'] == 5)
    cnt_mid      = sum(1 for w in words if 3 <= w['mastery_level'] < 5)
    cnt_low      = sum(1 for w in words if w['mastery_level'] <= 2)
    stats = {
        # Заголовочная статистика
        'total':    len(words),
        'mastered': cnt_mastered,
        'learning': cnt_mid,
        'low':      sum(1 for w in words if 0 < w['mastery_level'] < 3),
        'new':      sum(1 for w in words if w['mastery_level'] == 0),
        # Счётчики для кнопок-фильтров
        'cnt_all':      len(words),
        'cnt_low':      cnt_low,
        'cnt_mid':      cnt_mid,
        'cnt_mastered': cnt_mastered,
    }

    return templates.TemplateResponse(
        'dashboard/words/rating.html',
        {'request': request, 'words': words, 'user': current_user, 'stats': stats}
    )