from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Form

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.exercise_service import ExerciseService
from app.services.lesson_service import LessonService
from app.schemas.exercise import ExerciseCheckRequest

router = APIRouter(prefix='/dashboard/exercises', tags=['dashboard_exercises'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/lesson/{lesson_id}', response_class=HTMLResponse)
def exercises_page(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Страница с упражнениями урока"""
    exercise_service = ExerciseService(db)
    lesson_service = LessonService(db)
    
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    exercises = exercise_service.get_by_lesson(lesson_id)
    
    return templates.TemplateResponse('dashboard/exercises/exercises_page.html', {
        'request': request,
        'lesson': lesson,
        'exercises': exercises,
        'user': current_user
    })


@router.post('/check')
def check_exercise(
    exercise_id: int = Form(...),
    selected_option: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Проверка ответа на упражнение"""
    exercise_service = ExerciseService(db)
    result = exercise_service.check(exercise_id, selected_option)
    return result
