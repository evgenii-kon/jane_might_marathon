from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Annotated
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi import Form, HTTPException
from app.dependencies.auth import get_current_admin
from app.models.user import User

from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonResponse, LessonUpdate
from app.repositories.lesson_repository import LessonRepository
from app.services.lesson_service import LessonService

router = APIRouter(prefix='/admin/lessons', tags=['admin', 'lesson'])

templates = Jinja2Templates(directory = 'app/templates')


@router.get('/', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_lessons(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
    ):
    lesson_service = LessonService(db)
    all_lessons = lesson_service.get_all_lessons()
    return templates.TemplateResponse('admin/lessons/lessons_list.html', {"request": request, 'lessons': all_lessons})


@router.get('/create', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def create_lesson_get(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
    ):
    return templates.TemplateResponse('admin/lessons/lesson_create.html', {'request': request})


@router.post('/create', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_lesson_post(
    request: Request,
    lesson_data: Annotated[LessonCreate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
    ):
    lesson_service = LessonService(db)
    lesson = lesson_service.create_lesson(lesson_data)
    return RedirectResponse(url='/admin/lessons', status_code=302)


@router.get('/{lesson_id}/update', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def update_lesson_get(
    request: Request,
    lesson_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
    ):
    lesson_service = LessonService(db)
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'lesson with id = {lesson_id} not found'
        )
    return templates.TemplateResponse('admin/lessons/lesson_edit.html', {'request': request, 'lesson': lesson})


@router.post('/{lesson_id}/update', status_code=status.HTTP_200_OK)
def update_lesson_post(
    request: Request,
    lesson_id: int,
    lesson_data: Annotated[LessonUpdate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
    ):
    lesson_service = LessonService(db)
    lesson = lesson_service.update_lesson(lesson_id, lesson_data)
    return RedirectResponse(url='/admin/lesson/lessons_list', status_code=302)


@router.get('/{lesson_id}/delete', response_class=HTMLResponse)
def delete_lesson_get(
    request: Request,
    lesson_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    lesson_service = LessonService(db)
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    return templates.TemplateResponse('delete_lesson_confirm.html', {'request': request, 'lesson': lesson})


@router.post('/{lesson_id}/delete')
def delete_lesson_post(
    lesson_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    LessonService(db).delete_lesson(lesson_id)
    return RedirectResponse(url='/admin/lesson/all_lessons', status_code=302)