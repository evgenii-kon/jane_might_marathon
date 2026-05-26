import random

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.exercise_service import ExerciseService
from app.services.lesson_service import LessonService
from app.services.user_exercise_progress_service import UserExerciseProgressService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.csrf import get_csrf_token

router = APIRouter(prefix="/dashboard/exercises", tags=["dashboard_exercises"])
templates = Jinja2Templates(directory="app/templates")


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (асинхронные) ==========


async def _get_lesson_or_404(lesson_service, lesson_id: int):
    """Получить урок или вернуть 404"""
    lesson = await lesson_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return lesson


async def _check_lesson_completed(progress_service, user_id: int, lesson_id: int):
    """Проверить, что урок завершён, иначе ошибка 403"""
    if not await progress_service.is_lesson_completed(user_id, lesson_id):
        raise HTTPException(403, "Сначала нужно завершить урок")


def _get_current_exercise(exercises, completed_ids):
    """Найти первое невыполненное упражнение (синхронная, только работа со списками)"""
    for ex in exercises:
        if ex.id not in completed_ids:
            return ex
    return None


def _get_progress_stats(completed_ids, exercises):
    """Подсчитать статистику прогресса (синхронная)"""
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
    """Получить словарь вариантов ответов (синхронная)"""
    return {
        1: exercise.option_1,
        2: exercise.option_2,
        3: exercise.option_3,
        4: exercise.option_4,
    }


# ========== ОСНОВНЫЕ РОУТЫ ==========


@router.get("/lesson/{lesson_id}", response_class=HTMLResponse)
async def exercises_quiz(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Пошаговое прохождение упражнений урока"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)
    progress_service = UserExerciseProgressService(db)

    # 1. Проверяем урок
    lesson = await _get_lesson_or_404(lesson_service, lesson_id)

    # 2. Проверяем, что урок завершён
    await _check_lesson_completed(progress_service, current_user.id, lesson_id)

    # 3. Получаем упражнения
    exercises = await exercise_service.get_exercises_by_lesson(lesson_id)
    if not exercises:
        return templates.TemplateResponse(
            "dashboard/exercises/no_exercises.html",
            {"request": request, "lesson": lesson, "user": current_user},
        )

    # 4. Находим текущее упражнение
    completed_ids = await progress_service.get_completed_exercise_ids(
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

    # 7. Перемешиваем варианты ответов (data-option хранит оригинальный номер)
    options = [
        (1, current_exercise.option_1),
        (2, current_exercise.option_2),
        (3, current_exercise.option_3),
        (4, current_exercise.option_4),
    ]
    random.shuffle(options)

    return templates.TemplateResponse(
        "dashboard/exercises/exercises_quiz.html",
        {
            "request": request,
            "lesson": lesson,
            "exercise": current_exercise,
            "shuffled_options": options,
            "current_index": stats["current_index"],
            "total_count": stats["total_count"],
            "progress_percent": stats["percent"],
            "completed_count": stats["completed_count"],
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/lesson/{lesson_id}/check")
async def check_exercise_answer(
    lesson_id: int,
    exercise_id: int = Form(...),
    selected_option: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Проверка ответа на упражнение (AJAX)"""
    exercise_service = ExerciseService(db)
    progress_service = UserExerciseProgressService(db)

    # 1. Получаем упражнение
    exercise = await exercise_service.get_exercise_by_id(exercise_id)
    if not exercise:
        return {"error": "Exercise not found", "is_correct": False}

    # 2. Проверяем ответ
    is_correct = selected_option == exercise.correct_answer

    # 3. Сохраняем прогресс если правильно
    if is_correct and not await progress_service.is_exercise_completed(
        current_user.id, exercise_id
    ):
        await progress_service.mark_exercise_completed(current_user.id, exercise_id)

    # 4. Получаем тексты вариантов
    option_map = _get_option_map(exercise)

    # 5. Проверяем, есть ли ещё упражнения
    exercises = await exercise_service.get_exercises_by_lesson(lesson_id)
    completed_ids = await progress_service.get_completed_exercise_ids(
        current_user.id, lesson_id
    )
    has_next = len(completed_ids) < len(exercises)

    # 6. Если все упражнения впервые пройдены — ставим постоянный флаг
    if not has_next:
        lesson_progress_service = UserLessonProgressService(db)
        await lesson_progress_service.mark_exercises_ever_completed(
            current_user.id, lesson_id
        )

    return {
        "is_correct": is_correct,
        "correct_answer": exercise.correct_answer,
        "correct_answer_text": option_map.get(exercise.correct_answer, ""),
        "explanation": exercise.explanation,
        "has_next": has_next,
        "completed_count": len(completed_ids),
        "total_count": len(exercises),
    }


@router.post("/lesson/{lesson_id}/reset")
async def exercises_reset(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сбросить прогресс упражнений урока и перейти к прохождению заново"""
    lesson_service = LessonService(db)
    progress_service = UserExerciseProgressService(db)

    await _get_lesson_or_404(lesson_service, lesson_id)
    await progress_service.reset_lesson_exercises(current_user.id, lesson_id)

    return RedirectResponse(
        url=f"/dashboard/exercises/lesson/{lesson_id}", status_code=302
    )


@router.get("/lesson/{lesson_id}/completed", response_class=HTMLResponse)
async def exercises_completed(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Страница завершения всех упражнений"""
    lesson_service = LessonService(db)
    progress_service = UserExerciseProgressService(db)

    lesson = await _get_lesson_or_404(lesson_service, lesson_id)
    progress = await progress_service.get_lesson_progress(current_user.id, lesson_id)

    return templates.TemplateResponse(
        "dashboard/exercises/exercises_completed.html",
        {
            "request": request,
            "lesson": lesson,
            "progress": progress,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )