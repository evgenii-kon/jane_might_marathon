from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.services.user_service import UserService
from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.user_lesson_progress_service import UserLessonProgressService


router = APIRouter(prefix='/dashboard/lessons', tags=['dashboard'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/{lesson_id}', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def lesson_detail(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)


    lesson = lesson_service.get_lesson_by_id(lesson_id)

    progress_service.mark_lesson_as_started(current_user.id, lesson_id)
    
    is_started = progress_service.is_lesson_started(current_user.id, lesson_id)
    is_completed = progress_service.is_lesson_completed(current_user.id, lesson_id)

    return templates.TemplateResponse('dashboard/lessons/lesson_detail.html', {
        'request': request,
        'lesson': lesson,
        'is_started': is_started,
        'is_completed': is_completed,
        'user': current_user
    })

@router.post('/{lesson_id}/complete')
def complete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    """Отметить урок как пройденный и вернуться к списку уроков недели"""
    progress_service = UserLessonProgressService(db)
    lesson_service = LessonService(db)
    
    # Получаем урок, чтобы узнать week_id
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    
    # Отмечаем урок пройденным
    progress_service.mark_lesson_as_completed(current_user.id, lesson_id)
    
    # Редирект обратно на страницу недели
    return RedirectResponse(url=f'/dashboard/weeks/{lesson.week_id}', status_code=302)