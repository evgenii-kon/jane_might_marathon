from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.user_week_progress_service import UserWeekProgressService
from app.services.user_exercise_progress_service import UserExerciseProgressService
from app.services.user_lesson_progress_service import UserLessonProgressService

router = APIRouter(prefix="/dashboard/weeks", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{week_id}", response_class=HTMLResponse)
async def week_detail(
    request: Request,
    week_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    lesson_service = LessonService(db)
    lesson_progress_service = UserLessonProgressService(db)
    week_progress_service = UserWeekProgressService(db)
    exercise_progress_service = UserExerciseProgressService(db)

    week = await week_service.get_week_by_id(week_id)
    if not week:
        raise HTTPException(404, "Week not found")

    # Определяем, заблокирована ли неделя
    user_week_prog = await week_progress_service.repository.get_by_user_and_week(
        current_user.id, week_id
    )
    if user_week_prog:
        now = datetime.now(timezone.utc)
        opens_at = user_week_prog.opens_at
        if opens_at.tzinfo is None:
            opens_at = opens_at.replace(tzinfo=timezone.utc)
        is_locked = now < opens_at
    else:
        is_locked = week.number != 1

    lessons = await lesson_service.get_lessons_by_week(week_id)

    # Batch-загрузка прогресса уроков (2 запроса вместо 2*N)
    completed_ids = set(await lesson_progress_service.get_completed_lesson_ids(current_user.id))
    started_ids = set(await lesson_progress_service.get_started_lesson_ids(current_user.id))

    # Batch-загрузка прогресса упражнений (2 запроса вместо 2*N)
    lesson_ids = [lesson.id for lesson in lessons]
    exercises_progress = await exercise_progress_service.get_lessons_progress(
        current_user.id, lesson_ids
    )

    lessons_with_progress = []
    for lesson in lessons:
        ep = exercises_progress.get(lesson.id)
        ex_total = ep.total if ep else 0
        ex_completed = ep.completed if ep else 0

        lessons_with_progress.append({
            "id": lesson.id,
            "name": lesson.name,
            "order_in_week": lesson.order_in_week,
            "description": getattr(lesson, "description", None),
            "is_started": lesson.id in started_ids,
            "is_completed": lesson.id in completed_ids,
            "exercises_total": ex_total,
            "exercises_completed": ex_completed,
            "all_exercises_completed": ex_completed == ex_total and ex_total > 0,
        })

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
            "is_locked": is_locked,
            "user": current_user,
        },
    )
