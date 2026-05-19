from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from datetime import datetime, timezone

from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.user_week_progress_service import UserWeekProgressService
from app.services.user_exercise_progress_service import UserExerciseProgressService
from app.services.user_lesson_progress_service import UserLessonProgressService


router = APIRouter(prefix="/dashboard/weeks", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{week_id}", response_class=HTMLResponse)
def week_detail(
    request: Request,
    week_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    week_service = WeekService(db)
    lesson_service = LessonService(db)
    lesson_progress_service = UserLessonProgressService(db)
    week_progress_service = UserWeekProgressService(db)

    week = week_service.get_week_by_id(week_id)
    if not week:
        raise HTTPException(404, "Week not found")

    #user_week_progress = week_progress_service.get_or_create(current_user.id, week_id)

    lessons = lesson_service.get_lessons_by_week(week_id)
    lessons_with_progress = []
    for lesson in lessons:
        is_started = lesson_progress_service.is_lesson_started(
            current_user.id, lesson.id
        )
        is_completed = lesson_progress_service.is_lesson_completed(
            current_user.id, lesson.id
        )

        # Получаем прогресс упражнений для урока (опционально)
        exercise_progress_service = UserExerciseProgressService(db)
        exercise_progress = exercise_progress_service.get_lesson_progress(
            current_user.id, lesson.id
        )

        lessons_with_progress.append(
            {
                "id": lesson.id,
                "name": lesson.name,
                "order_in_week": lesson.order_in_week,
                "description": getattr(lesson, "description", None),
                "is_started": is_started,
                "is_completed": is_completed,
                "exercises_total": exercise_progress.total,
                "exercises_completed": exercise_progress.completed,
                "all_exercises_completed": exercise_progress.completed
                == exercise_progress.total
                and exercise_progress.total > 0,
            }
        )

    total_lessons = len(lessons)
    completed_lessons = sum(1 for l in lessons_with_progress if l["is_completed"])
    progress_percent = (
        int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    )

    return templates.TemplateResponse(
        "dashboard/weeks/week_detail.html",
        {
            "request": request,
            "week": week,
            "lessons": lessons_with_progress,
            "total_count": total_lessons,
            "completed_count": completed_lessons,
            "progress_percent": progress_percent,
            "is_locked": False,
            "user": current_user,
        },
    )
