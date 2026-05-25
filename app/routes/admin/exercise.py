from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.exercise_service import ExerciseService
from app.services.lesson_service import LessonService
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate

router = APIRouter(prefix="/admin/exercises", tags=["admin_exercises"])
templates = Jinja2Templates(directory="app/templates")


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
    lessons = await lesson_service.get_all_lessons()

    return templates.TemplateResponse(
        "admin/exercises/exercises_create.html",
        {
            "request": request,
            "lessons": lessons,
            "selected_lesson_id": lesson_id,
            "user": current_user,
            "form_data": {},
            "csrf_token": getattr(request.state, "csrf_token", request.cookies.get("csrftoken", "")),
        },
    )


@router.post("/create")
async def create_exercise(
    request: Request,
    lesson_id: int = Form(...),
    question_description: str = Form(...),
    question_text: str = Form(...),
    option_1: str = Form(...),
    option_2: str = Form(...),
    option_3: str = Form(...),
    option_4: str = Form(...),
    correct_answer: int = Form(...),
    order_in_lesson: int = Form(0),
    explanation: str = Form(None),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Создание упражнения"""
    exercise_service = ExerciseService(db)

    try:
        exercise_data = ExerciseCreate(
            lesson_id=lesson_id,
            question_description=question_description,
            question_text=question_text,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_answer=correct_answer,
            explanation=explanation,
            order_in_lesson=order_in_lesson,
        )

        await exercise_service.create_exercise(exercise_data)
        return RedirectResponse(
            url=f"/admin/exercises?lesson_id={lesson_id}", status_code=303
        )

    except Exception as e:
        lesson_service = LessonService(db)
        lessons = await lesson_service.get_all_lessons()

        return templates.TemplateResponse(
            "admin/exercises/exercises_create.html",
            {
                "request": request,
                "lessons": lessons,
                "selected_lesson_id": lesson_id,
                "error": str(e),
                "form_data": {
                    "question_description": question_description,
                    "question_text": question_text,
                    "option_1": option_1,
                    "option_2": option_2,
                    "option_3": option_3,
                    "option_4": option_4,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                    "order_in_lesson": order_in_lesson,
                },
                "user": current_user,
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

    exercise = await exercise_service.get_exercise_by_id(exercise_id)
    lessons = await lesson_service.get_all_lessons()

    return templates.TemplateResponse(
        "admin/exercises/exercises_edit.html",
        {
            "request": request,
            "exercise": exercise,
            "lessons": lessons,
            "user": current_user,
            "csrf_token": getattr(request.state, "csrf_token", request.cookies.get("csrftoken", "")),
        },
    )


@router.post("/{exercise_id}/edit")
async def edit_exercise(
    request: Request,
    exercise_id: int,
    lesson_id: int = Form(...),
    question_description: str = Form(...),
    question_text: str = Form(...),
    option_1: str = Form(...),
    option_2: str = Form(...),
    option_3: str = Form(...),
    option_4: str = Form(...),
    correct_answer: int = Form(...),
    order_in_lesson: int = Form(0),
    explanation: str = Form(None),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Обновление упражнения"""
    exercise_service = ExerciseService(db)

    try:
        update_data = ExerciseUpdate(
            lesson_id=lesson_id,
            question_description=question_description,
            question_text=question_text,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_answer=correct_answer,
            explanation=explanation,
            order_in_lesson=order_in_lesson,
        )

        updated = await exercise_service.update_exercise(exercise_id, update_data)
        return RedirectResponse(
            url=f"/admin/exercises?lesson_id={updated.lesson_id}", status_code=303
        )

    except Exception as e:
        lesson_service = LessonService(db)
        lessons = await lesson_service.get_all_lessons()
        exercise = await exercise_service.get_exercise_by_id(exercise_id)

        return templates.TemplateResponse(
            "admin/exercises/exercises_edit.html",
            {
                "request": request,
                "exercise": exercise,
                "lessons": lessons,
                "error": str(e),
                "form_data": {
                    "question_description": question_description,
                    "question_text": question_text,
                    "option_1": option_1,
                    "option_2": option_2,
                    "option_3": option_3,
                    "option_4": option_4,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                    "order_in_lesson": order_in_lesson,
                },
                "user": current_user,
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
            "csrf_token": getattr(request.state, "csrf_token", request.cookies.get("csrftoken", "")),
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