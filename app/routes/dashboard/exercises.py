from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.exercise_service import ExerciseService
from app.services.lesson_service import LessonService
from app.services.user_exercise_progress_service import UserExerciseProgressService

router = APIRouter(prefix="/dashboard/exercises", tags=["dashboard_exercises"])
templates = Jinja2Templates(directory="app/templates")


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========


def _get_lesson_or_404(lesson_service, lesson_id: int):
    """Получить урок или вернуть 404"""
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return lesson


def _check_lesson_completed(progress_service, user_id: int, lesson_id: int):
    """Проверить, что урок завершён, иначе ошибка 403"""
    if not progress_service.is_lesson_completed(user_id, lesson_id):
        raise HTTPException(403, "Сначала нужно завершить урок")


def _get_current_exercise(exercises, completed_ids):
    """Найти первое невыполненное упражнение"""
    for ex in exercises:
        if ex.id not in completed_ids:
            return ex
    return None


def _get_progress_stats(completed_ids, exercises):
    """Подсчитать статистику прогресса"""
    completed_count = len(completed_ids)
    total_count = len(exercises)
    percent = int((completed_count / total_count) * 100) if total_count > 0 else 0
    return {
        "completed_count": completed_count,
        "total_count": total_count,
        "percent": percent,
        "current_index": completed_count + 1,
    }


def _get_option_map(exercise):
    """Получить словарь вариантов ответов"""
    return {
        1: exercise.option_1,
        2: exercise.option_2,
        3: exercise.option_3,
        4: exercise.option_4,
    }


# ========== ОСНОВНЫЕ РОУТЫ ==========


@router.get("/lesson/{lesson_id}", response_class=HTMLResponse)
def exercises_quiz(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Пошаговое прохождение упражнений урока"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)
    progress_service = UserExerciseProgressService(db)

    # 1. Проверяем урок
    lesson = _get_lesson_or_404(lesson_service, lesson_id)

    # 2. Проверяем, что урок завершён
    _check_lesson_completed(progress_service, current_user.id, lesson_id)

    # 3. Получаем упражнения
    exercises = exercise_service.get_exercises_by_lesson(lesson_id)
    if not exercises:
        return templates.TemplateResponse(
            "dashboard/exercises/no_exercises.html",
            {"request": request, "lesson": lesson, "user": current_user},
        )

    # 4. Находим текущее упражнение
    completed_ids = progress_service.get_completed_exercise_ids(
        current_user.id, lesson_id
    )
    current_exercise = _get_current_exercise(exercises, completed_ids)

    # 5. Если все выполнены — редирект
    if not current_exercise:
        return RedirectResponse(
            url=f"/dashboard/exercises/lesson/{lesson_id}/completed", status_code=302
        )

    # 6. Статистика для отображения
    stats = _get_progress_stats(completed_ids, exercises)

    return templates.TemplateResponse(
        "dashboard/exercises/exercises_quiz.html",
        {
            "request": request,
            "lesson": lesson,
            "exercise": current_exercise,
            "current_index": stats["current_index"],
            "total_count": stats["total_count"],
            "progress_percent": stats["percent"],
            "completed_count": stats["completed_count"],
            "user": current_user,
        },
    )


@router.post("/lesson/{lesson_id}/check")
def check_exercise_answer(
    lesson_id: int,
    exercise_id: int = Form(...),
    selected_option: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Проверка ответа на упражнение (AJAX)"""
    exercise_service = ExerciseService(db)
    progress_service = UserExerciseProgressService(db)

    # 1. Получаем упражнение
    exercise = exercise_service.get_exercise_by_id(exercise_id)
    if not exercise:
        return {"error": "Exercise not found", "is_correct": False}

    # 2. Проверяем ответ
    is_correct = selected_option == exercise.correct_answer

    # 3. Сохраняем прогресс если правильно
    if is_correct and not progress_service.is_exercise_completed(
        current_user.id, exercise_id
    ):
        progress_service.mark_exercise_completed(current_user.id, exercise_id)

    # 4. Получаем тексты вариантов
    option_map = _get_option_map(exercise)

    # 5. Проверяем, есть ли ещё упражнения
    exercises = exercise_service.get_exercises_by_lesson(lesson_id)
    completed_ids = progress_service.get_completed_exercise_ids(
        current_user.id, lesson_id
    )
    has_next = len(completed_ids) < len(exercises)

    return {
        "is_correct": is_correct,
        "correct_answer": exercise.correct_answer,
        "correct_answer_text": option_map.get(exercise.correct_answer, ""),
        "explanation": exercise.explanation,
        "has_next": has_next,
        "completed_count": len(completed_ids),
        "total_count": len(exercises),
    }


@router.get("/lesson/{lesson_id}/completed", response_class=HTMLResponse)
def exercises_completed(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Страница завершения всех упражнений"""
    lesson_service = LessonService(db)
    progress_service = UserExerciseProgressService(db)

    lesson = _get_lesson_or_404(lesson_service, lesson_id)
    progress = progress_service.get_lesson_progress(current_user.id, lesson_id)

    return templates.TemplateResponse(
        "dashboard/exercises/exercises_completed.html",
        {
            "request": request,
            "lesson": lesson,
            "progress": progress,
            "user": current_user,
        },
    )
