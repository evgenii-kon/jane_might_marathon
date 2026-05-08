from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date, datetime, timezone
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.services.word_trainer_service import WordTrainerService

router = APIRouter(prefix='/dashboard', tags=['dashboard'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Сервисы
    week_service = WeekService(db)
    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)
    word_trainer_service = WordTrainerService(db)

    # Данные пользователя
    user = current_user
    today = date.today()

    days_after_start = (today - user.created_at.date()).days

    
    # Все недели
    weeks = week_service.get_all_weeks()
    
    # Общий прогресс по урокам
    total_lessons = lesson_service.get_lessons_count()
    completed_lessons = progress_service.get_completed_count_by_user(user.id)
    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    # Прогресс по неделям
    weeks_with_progress = []
    for week in weeks:
        week_progress = progress_service.get_week_progress(current_user.id, week.id)
        
        # Простая логика: неделя 0 и 1 открыты, остальные заблокированы
        is_locked = week.number > 1
        
        weeks_with_progress.append({
            'id': week.id,
            'number': week.number,
            'short_description': week.short_description,
            'total_lessons': week_progress.total_lessons,
            'completed_lessons': week_progress.completed_lessons,
            'progress_percent': week_progress.progress_percent,
            'is_locked': is_locked,
            'is_completed': week_progress.is_week_completed
        })
    
    # Статистика по словам
    due_today = word_trainer_service.get_due_count(user.id)
    mastery_stats = word_trainer_service.get_mastery_stats(user.id)
    mastered_words = mastery_stats.get(5, 0)  # уровень 5 = мастер
    learned_words = sum(v for k, v in mastery_stats.items() if k >= 3)  # уровни 3-5
    total_words = word_trainer_service.get_total_words_count()
    
    return templates.TemplateResponse('dashboard/index.html', {
        'request': request,
        'user': current_user,
        'days_after_start': days_after_start,
        'weeks': weeks_with_progress,
        'total_completed': completed_lessons,
        'total_lessons': total_lessons,
        'progress_percent': progress_percent,
        'due_today': due_today,
        'mastered_words': mastered_words,
        'learned_words': learned_words,
        'total_words': total_words
    })