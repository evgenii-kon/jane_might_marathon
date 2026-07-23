import json
import random

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.subscription import require_feature_or_trial_lesson
from app.models.user import User
from app.services.exercise_service import ExerciseService
from app.services.lesson_service import LessonService
from app.services.user_exercise_progress_service import UserExerciseProgressService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.services.user_activity_service import UserActivityService
from app.repositories.word_repository import WordRepository
from app.csrf import get_csrf_token
from app.services.exercise_service import _normalize_translate_answer

router = APIRouter(prefix="/dashboard/exercises", tags=["dashboard_exercises"])

TEMPLATE_BY_TYPE = {
    "quiz": "dashboard/exercises/exercises_quiz.html",
    "choose_hanzi": "dashboard/exercises/exercises_quiz.html",
    "matching_pairs": "dashboard/exercises/exercises_matching.html",
    "build_word": "dashboard/exercises/exercises_build_word.html",
    "fill_blank": "dashboard/exercises/exercises_fill_blank.html",
    "audio_quiz": "dashboard/exercises/exercises_audio_quiz.html",
    "translate": "dashboard/exercises/exercises_translate.html",
    "fill_blank_open": "dashboard/exercises/exercises_fill_blank_open.html",
    "multi_select": "dashboard/exercises/exercises_multi_select.html",
}


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


def _option_text(options, index):
    if index is None or index < 0 or index >= len(options):
        return ""
    return options[index]


# ========== ОСНОВНЫЕ РОУТЫ ==========


@router.get("/lesson/{lesson_id}", response_class=HTMLResponse)
async def exercises_quiz(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature_or_trial_lesson("exercises")),
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

    template_name = TEMPLATE_BY_TYPE.get(current_exercise.type)
    if not template_name:
        raise HTTPException(500, f"Unknown exercise type: {current_exercise.type}")

    context = {
        "request": request,
        "lesson": lesson,
        "exercise": current_exercise,
        "current_index": stats["current_index"],
        "total_count": stats["total_count"],
        "progress_percent": stats["percent"],
        "completed_count": stats["completed_count"],
        "user": current_user,
        "csrf_token": get_csrf_token(request),
    }

    if current_exercise.type in ("quiz", "choose_hanzi"):
        # Перемешиваем варианты ответов (data-option хранит оригинальный 0-based индекс)
        options = current_exercise.config.get("options", [])
        shuffled_options = list(enumerate(options))
        random.shuffle(shuffled_options)
        context["shuffled_options"] = shuffled_options
        context["is_choose_hanzi"] = current_exercise.type == "choose_hanzi"

    elif current_exercise.type == "audio_quiz":
        options = current_exercise.config.get("options", [])
        shuffled_options = list(enumerate(options))
        random.shuffle(shuffled_options)
        context["shuffled_options"] = shuffled_options
        context["audio_url"] = current_exercise.config.get("audio_url", "")

    elif current_exercise.type == "matching_pairs":
        if "pairs" in current_exercise.config:
            pairs = current_exercise.config["pairs"]
            context["words"] = [
                {"id": i, "word": p["left"], "translation": p["right"]}
                for i, p in enumerate(pairs)
            ]
            context["pair_count"] = len(pairs)
        else:
            word_ids = current_exercise.config.get("word_ids", [])
            word_repo = WordRepository(db)
            words = await word_repo.get_by_ids(word_ids)
            words_by_id = {w.id: w for w in words}
            ordered_words = [words_by_id[wid] for wid in word_ids if wid in words_by_id]
            context["words"] = [
                {"id": w.id, "word": w.hanzi, "translation": w.translation}
                for w in ordered_words
            ]
            context["pair_count"] = current_exercise.config.get("pair_count", 4)

    return templates.TemplateResponse(template_name, context)


@router.post("/lesson/{lesson_id}/check")
async def check_exercise_answer(
    lesson_id: int,
    exercise_id: int = Form(...),
    selected_option: int = Form(None),
    user_answer: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_feature_or_trial_lesson("exercises")),
):
    """Проверка ответа на упражнение (AJAX)"""
    exercise_service = ExerciseService(db)
    progress_service = UserExerciseProgressService(db)

    # 1. Получаем упражнение
    exercise = await exercise_service.get_exercise_by_id(exercise_id)
    if not exercise:
        return {"error": "Exercise not found", "is_correct": False}

    if exercise.lesson_id != lesson_id:
        raise HTTPException(403, "Exercise does not belong to this lesson")

    config = exercise.config or {}
    options = config.get("options", [])
    correct_answer = None
    correct_answer_text = ""

    # 2. Проверяем ответ (логика зависит от типа упражнения)
    if exercise.type in ("quiz", "choose_hanzi", "fill_blank", "audio_quiz"):
        correct_answer = config.get("correct")
        is_correct = selected_option == correct_answer
        correct_answer_text = _option_text(options, correct_answer)
    elif exercise.type == "matching_pairs":
        # Все пары уже проверены на клиенте — здесь просто фиксируем завершение
        is_correct = True
    elif exercise.type == "build_word":
        correct_answer = config.get("answer", "")
        correct_answer_text = correct_answer
        is_correct = user_answer == correct_answer
    elif exercise.type == "translate":
        correct_answer = config.get("answer", "")
        correct_answer_text = correct_answer
        is_correct = _normalize_translate_answer(user_answer or "") == _normalize_translate_answer(correct_answer)
    elif exercise.type == "multi_select":
        statements = config.get("statements", [])
        correct = sorted(config.get("correct", []))
        try:
            selected = sorted(set(json.loads(user_answer or "[]")))
        except (TypeError, ValueError):
            selected = []
        is_correct = selected == correct
        correct_answer_text = " · ".join(statements[i] for i in correct if 0 <= i < len(statements))
    elif exercise.type == "fill_blank_open":
        blanks = config.get("blanks", [])
        try:
            user_blanks = json.loads(user_answer or "[]")
        except (TypeError, ValueError):
            user_blanks = []
        is_correct = len(user_blanks) == len(blanks) and all(
            (u or "").strip().lower() == (b or "").strip().lower()
            for u, b in zip(user_blanks, blanks)
        )
        correct_answer_text = " · ".join(b if b else "(пусто)" for b in blanks)
    else:
        is_correct = False

    # 3. Сохраняем прогресс если правильно
    if is_correct and not await progress_service.is_exercise_completed(
        current_user.id, exercise_id
    ):
        await progress_service.mark_exercise_completed(current_user.id, exercise_id)
        activity_service = UserActivityService(db)
        await activity_service.record_activity(current_user.id)

    # 4. Проверяем, есть ли ещё упражнения
    exercises = await exercise_service.get_exercises_by_lesson(lesson_id)
    completed_ids = await progress_service.get_completed_exercise_ids(
        current_user.id, lesson_id
    )
    has_next = len(completed_ids) < len(exercises)

    # 5. Если все упражнения впервые пройдены — ставим постоянный флаг
    if not has_next:
        lesson_progress_service = UserLessonProgressService(db)
        await lesson_progress_service.mark_exercises_ever_completed(
            current_user.id, lesson_id
        )

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "correct_answer_text": correct_answer_text,
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
    _: User = Depends(require_feature_or_trial_lesson("exercises")),
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
    _: User = Depends(require_feature_or_trial_lesson("exercises")),
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
