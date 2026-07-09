from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.exercise_service import ExerciseService
from app.services.lesson_service import LessonService
from app.services.word_service import WordService
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, EXERCISE_TYPES
from app.csrf import get_csrf_token

router = APIRouter(prefix="/admin/exercises", tags=["admin_exercises"])
api_router = APIRouter(prefix="/admin/api", tags=["admin_api"])
templates = Jinja2Templates(directory="app/templates")


EXERCISE_TYPE_LABELS = {
    "quiz": "🎯 Выбор перевода",
    "choose_hanzi": "🀄 Выбор иероглифа",
    "matching_pairs": "🃏 Сопоставление пар",
    "build_word": "🔧 Собери слово",
    "fill_blank": "✏️ Заполни пропуск",
}


def _parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


async def _extract_exercise_fields(request: Request) -> dict:
    """Собрать question_text/config из формы в зависимости от exercise_type."""
    form = await request.form()
    exercise_type = (form.get("exercise_type") or "").strip()

    if exercise_type not in EXERCISE_TYPES:
        raise ValueError("Выберите корректный тип упражнения")

    lesson_id = _parse_int(form.get("lesson_id"))
    order_in_lesson = _parse_int(form.get("order_in_lesson"), 0)
    explanation = (form.get("explanation") or "").strip() or None

    question_text = None
    config: dict = {}

    if exercise_type in ("quiz", "choose_hanzi"):
        question_text = (form.get("qh_question_text") or "").strip()
        options = [(form.get(f"qh_option_{i}") or "").strip() for i in range(1, 5)]
        correct_raw = _parse_int(form.get("qh_correct_answer"))
        word_id = _parse_int(form.get("qh_word_id"))

        if not question_text or not all(options) or correct_raw is None:
            raise ValueError("Заполните текст вопроса, все 4 варианта и правильный ответ")

        config = {"word_id": word_id, "options": options, "correct": correct_raw - 1}

    elif exercise_type == "fill_blank":
        sentence = (form.get("fb_sentence") or "").strip()
        options = [(form.get(f"fb_option_{i}") or "").strip() for i in range(1, 5)]
        correct_raw = _parse_int(form.get("fb_correct_answer"))

        if not sentence or not all(options) or correct_raw is None:
            raise ValueError("Заполните предложение, все 4 варианта и правильный ответ")

        config = {"sentence": sentence, "options": options, "correct": correct_raw - 1}

    elif exercise_type == "build_word":
        parts = [p.strip() for p in (form.get("bw_parts") or "").split(",") if p.strip()]
        answer = (form.get("bw_answer") or "").strip()
        translation = (form.get("bw_translation") or "").strip()

        if not parts or not answer or not translation:
            raise ValueError("Заполните иероглифы, правильный ответ и перевод")

        config = {"parts": parts, "answer": answer, "translation": translation}

    elif exercise_type == "matching_pairs":
        word_ids = [int(v) for v in form.getlist("mp_word_ids") if v]
        pair_count = _parse_int(form.get("mp_pair_count")) or min(4, len(word_ids)) or 4

        if len(word_ids) < 4:
            raise ValueError("Выберите минимум 4 слова для сопоставления пар")

        config = {"pair_count": pair_count, "word_ids": word_ids}

    return {
        "lesson_id": lesson_id,
        "type": exercise_type,
        "question_text": question_text,
        "config": config,
        "explanation": explanation,
        "order_in_lesson": order_in_lesson or 0,
        "form_data": {
            "exercise_type": exercise_type,
            "lesson_id": lesson_id,
            "order_in_lesson": order_in_lesson,
            "explanation": explanation,
            "qh_question_text": form.get("qh_question_text"),
            "qh_word_id": form.get("qh_word_id"),
            "qh_option_1": form.get("qh_option_1"),
            "qh_option_2": form.get("qh_option_2"),
            "qh_option_3": form.get("qh_option_3"),
            "qh_option_4": form.get("qh_option_4"),
            "qh_correct_answer": form.get("qh_correct_answer"),
            "fb_sentence": form.get("fb_sentence"),
            "fb_option_1": form.get("fb_option_1"),
            "fb_option_2": form.get("fb_option_2"),
            "fb_option_3": form.get("fb_option_3"),
            "fb_option_4": form.get("fb_option_4"),
            "fb_correct_answer": form.get("fb_correct_answer"),
            "bw_parts": form.get("bw_parts"),
            "bw_answer": form.get("bw_answer"),
            "bw_translation": form.get("bw_translation"),
            "mp_pair_count": form.get("mp_pair_count"),
            "mp_word_ids": [int(v) for v in form.getlist("mp_word_ids") if v],
        },
    }


def _exercise_to_form_data(exercise) -> dict:
    """Развернуть exercise.config обратно в плоские поля формы (для предзаполнения на edit)."""
    config = exercise.config or {}
    fd = {
        "exercise_type": exercise.type,
        "lesson_id": exercise.lesson_id,
        "order_in_lesson": exercise.order_in_lesson,
        "explanation": exercise.explanation,
        "mp_word_ids": [],
    }

    if exercise.type in ("quiz", "choose_hanzi"):
        options = config.get("options", ["", "", "", ""])
        correct = config.get("correct")
        fd["qh_question_text"] = exercise.question_text
        fd["qh_word_id"] = config.get("word_id")
        for i in range(4):
            fd[f"qh_option_{i + 1}"] = options[i] if i < len(options) else ""
        fd["qh_correct_answer"] = str(correct + 1) if correct is not None else ""

    elif exercise.type == "fill_blank":
        options = config.get("options", ["", "", "", ""])
        correct = config.get("correct")
        fd["fb_sentence"] = config.get("sentence", "")
        for i in range(4):
            fd[f"fb_option_{i + 1}"] = options[i] if i < len(options) else ""
        fd["fb_correct_answer"] = str(correct + 1) if correct is not None else ""

    elif exercise.type == "build_word":
        fd["bw_parts"] = ", ".join(config.get("parts", []))
        fd["bw_answer"] = config.get("answer", "")
        fd["bw_translation"] = config.get("translation", "")

    elif exercise.type == "matching_pairs":
        fd["mp_pair_count"] = config.get("pair_count", 4)
        fd["mp_word_ids"] = config.get("word_ids", [])

    return fd


@router.get("/", response_class=HTMLResponse)
async def list_exercises(
    request: Request,
    lesson_id: int = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Список упражнений (фильтр по уроку)"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)

    lessons = await lesson_service.get_all_lessons()

    if lesson_id:
        exercises = await exercise_service.get_exercises_by_lesson(lesson_id)
        selected_lesson = await lesson_service.get_lesson_by_id(lesson_id)
    else:
        exercises = await exercise_service.get_all_exercises()
        selected_lesson = None

    return templates.TemplateResponse(
        "admin/exercises/exercises_list.html",
        {
            "request": request,
            "exercises": exercises,
            "lessons": lessons,
            "selected_lesson": selected_lesson,
            "lesson_id": lesson_id,
            "type_labels": EXERCISE_TYPE_LABELS,
            "user": current_user,
        },
    )


@router.get("/create", response_class=HTMLResponse)
async def create_exercise_form(
    request: Request,
    lesson_id: int = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Форма создания упражнения"""
    lesson_service = LessonService(db)
    word_service = WordService(db)
    lessons = await lesson_service.get_all_lessons()

    words = await word_service.get_words_by_lesson(lesson_id) if lesson_id else []

    return templates.TemplateResponse(
        "admin/exercises/exercises_create.html",
        {
            "request": request,
            "lessons": lessons,
            "selected_lesson_id": lesson_id,
            "exercise_types": EXERCISE_TYPES,
            "type_labels": EXERCISE_TYPE_LABELS,
            "lesson_words": words,
            "user": current_user,
            "form_data": {"exercise_type": "quiz", "lesson_id": lesson_id, "mp_word_ids": []},
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/create")
async def create_exercise(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Создание упражнения"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)
    word_service = WordService(db)

    fields = None
    try:
        fields = await _extract_exercise_fields(request)
        exercise_data = ExerciseCreate(
            lesson_id=fields["lesson_id"],
            type=fields["type"],
            question_text=fields["question_text"],
            config=fields["config"],
            explanation=fields["explanation"],
            order_in_lesson=fields["order_in_lesson"],
        )

        await exercise_service.create_exercise(exercise_data)
        return RedirectResponse(
            url=f"/admin/exercises?lesson_id={fields['lesson_id']}", status_code=303
        )

    except Exception as e:
        lessons = await lesson_service.get_all_lessons()
        form_data = fields["form_data"] if fields else {}
        lesson_id_for_words = form_data.get("lesson_id") if form_data else None
        words = await word_service.get_words_by_lesson(lesson_id_for_words) if lesson_id_for_words else []

        return templates.TemplateResponse(
            "admin/exercises/exercises_create.html",
            {
                "request": request,
                "lessons": lessons,
                "selected_lesson_id": form_data.get("lesson_id") if form_data else None,
                "exercise_types": EXERCISE_TYPES,
                "type_labels": EXERCISE_TYPE_LABELS,
                "lesson_words": words,
                "error": str(e),
                "form_data": form_data,
                "user": current_user,
                "csrf_token": get_csrf_token(request),
            },
        )


@router.get("/{exercise_id}/edit", response_class=HTMLResponse)
async def edit_exercise_form(
    request: Request,
    exercise_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Форма редактирования упражнения"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)
    word_service = WordService(db)

    exercise = await exercise_service.get_exercise_by_id(exercise_id)
    lessons = await lesson_service.get_all_lessons()

    words = []
    if exercise.type == "matching_pairs" and exercise.lesson_id:
        words = await word_service.get_words_by_lesson(exercise.lesson_id)

    return templates.TemplateResponse(
        "admin/exercises/exercises_edit.html",
        {
            "request": request,
            "exercise": exercise,
            "lessons": lessons,
            "exercise_types": EXERCISE_TYPES,
            "type_labels": EXERCISE_TYPE_LABELS,
            "lesson_words": words,
            "form_data": _exercise_to_form_data(exercise),
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{exercise_id}/edit")
async def edit_exercise(
    request: Request,
    exercise_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Обновление упражнения"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)
    word_service = WordService(db)

    fields = None
    try:
        fields = await _extract_exercise_fields(request)
        update_data = ExerciseUpdate(
            lesson_id=fields["lesson_id"],
            type=fields["type"],
            question_text=fields["question_text"],
            config=fields["config"],
            explanation=fields["explanation"],
            order_in_lesson=fields["order_in_lesson"],
        )

        updated = await exercise_service.update_exercise(exercise_id, update_data)
        return RedirectResponse(
            url=f"/admin/exercises?lesson_id={updated.lesson_id}", status_code=303
        )

    except Exception as e:
        lessons = await lesson_service.get_all_lessons()
        exercise = await exercise_service.get_exercise_by_id(exercise_id)
        form_data = fields["form_data"] if fields else _exercise_to_form_data(exercise)
        lesson_id_for_words = form_data.get("lesson_id") if form_data else exercise.lesson_id
        words = await word_service.get_words_by_lesson(lesson_id_for_words) if lesson_id_for_words else []

        return templates.TemplateResponse(
            "admin/exercises/exercises_edit.html",
            {
                "request": request,
                "exercise": exercise,
                "lessons": lessons,
                "exercise_types": EXERCISE_TYPES,
                "type_labels": EXERCISE_TYPE_LABELS,
                "lesson_words": words,
                "error": str(e),
                "form_data": form_data,
                "user": current_user,
                "csrf_token": get_csrf_token(request),
            },
        )


@router.get("/{exercise_id}/delete", response_class=HTMLResponse)
async def delete_exercise_confirm(
    request: Request,
    exercise_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Подтверждение удаления упражнения"""
    exercise_service = ExerciseService(db)
    exercise = await exercise_service.get_exercise_by_id(exercise_id)

    return templates.TemplateResponse(
        "admin/exercises/delete_confirm.html",
        {
            "request": request,
            "exercise": exercise,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{exercise_id}/delete")
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Удаление упражнения"""
    exercise_service = ExerciseService(db)
    exercise = await exercise_service.get_exercise_by_id(exercise_id)
    lesson_id = exercise.lesson_id

    await exercise_service.delete_exercise(exercise_id)

    return RedirectResponse(
        url=f"/admin/exercises?lesson_id={lesson_id}", status_code=303
    )


@api_router.get("/words")
async def api_words(
    lesson_id: int = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Слова для мультиселекта в форме упражнения matching_pairs"""
    word_service = WordService(db)
    words = (
        await word_service.get_words_by_lesson(lesson_id)
        if lesson_id
        else await word_service.get_all_words()
    )
    return JSONResponse(
        [{"id": w.id, "hanzi": w.hanzi, "translation": w.translation} for w in words]
    )
