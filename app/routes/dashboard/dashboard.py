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
from app.services.user_activity_service import UserActivityService
from app.services.word_of_day_service import get_word_of_day
from app.services.subscription_service import get_active_subscription, get_user_features
from app.dependencies.subscription import require_feature
from app.redis_client import get_redis

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


def days_word(n: int) -> str:
    if 11 <= n % 100 <= 19:
        return "дней"
    r = n % 10
    if r == 1:
        return "день"
    if 2 <= r <= 4:
        return "дня"
    return "дней"


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

    # Данные пользователя
    user = current_user
    sub = await get_active_subscription(db, current_user.id)
    active_plan = sub.plan if sub else None
    has_subscription = sub is not None
    user_features = await get_user_features(db, current_user)
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

    for week in weeks:
        week_progress = await progress_service.get_week_progress(current_user.id, week.id)

        if week.number == 1:
            is_locked = False
        else:
            is_locked = not has_subscription

        weeks_with_progress.append({
            "id": week.id,
            "number": week.number,
            "short_description": week.short_description,
            "total_lessons": week_progress.total_lessons,
            "completed_lessons": week_progress.completed_lessons,
            "progress_percent": week_progress.progress_percent,
            "is_locked": is_locked,
            "is_completed": week_progress.is_week_completed,
        })

    # "Сегодняшний урок" — первый непройденный урок пользователя
    all_lessons = await lesson_service.get_all_lessons()
    week_number_map = {w.id: w.number for w in weeks}
    completed_ids = set(await progress_service.get_completed_lesson_ids(user.id))

    all_lessons_sorted = sorted(
        all_lessons, key=lambda l: (week_number_map.get(l.week_id, 0), l.order_in_week)
    )

    today_lesson = None
    today_lesson_week_number = None
    for lesson in all_lessons_sorted:
        if lesson.id not in completed_ids:
            today_lesson = lesson
            today_lesson_week_number = week_number_map.get(lesson.week_id)
            break

    # Темп прохождения — только при активной подписке
    pace_label = None
    if sub:
        started_at = sub.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        days_since_payment = (datetime.now(timezone.utc) - started_at).days

        paid_completed = len(completed_ids)
        days_diff = abs(paid_completed - days_since_payment)

        if paid_completed > days_since_payment:
            pace_label = f"🚀 Вы опережаете график на {days_diff} {days_word(days_diff)}! Не бегите вперед, потратьте сегодня время на тренажеры или вспормите грамматику, которую уже прошли"
        elif paid_completed < days_since_payment:
            pace_label = f"⏰ Вы отстаёте от графика на {days_diff} {days_word(days_diff)}, стоит немного поднажать!"
        else:
            pace_label = "✅ Вы идёте прямо по графику!"

    # Статистика по словам
    due_today = await word_trainer_service.get_due_count(user.id)
    mastery_stats = await word_trainer_service.get_mastery_stats(user.id)
    mastered_words = mastery_stats.get(5, 0)
    learned_words = sum(v for k, v in mastery_stats.items() if k >= 3)
    total_words = await word_trainer_service.get_total_words_count(current_user.id)

    # Активность
    activity_service = UserActivityService(db)
    activity_data = await activity_service.get_year_activity(current_user.id)
    streak = await activity_service.get_streak(current_user.id)
    total_active_days = await activity_service.get_total_active_days(current_user.id)

    # Слово дня
    word_of_day = await get_word_of_day(db, get_redis())

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
            "activity_data": activity_data,
            "streak": streak,
            "total_days": total_active_days,
            "today_date": str(today_utc),
            "word_of_day": word_of_day,
            "has_subscription": has_subscription,
            "active_plan": active_plan,
            "user_features": user_features,
            "subscription": sub,
            "today_lesson": today_lesson,
            "today_lesson_week_number": today_lesson_week_number,
            "pace_label": pace_label,
        },
    )


@router.get('/words/rating', response_class=HTMLResponse)
async def word_rating(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("word_trainer")),
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