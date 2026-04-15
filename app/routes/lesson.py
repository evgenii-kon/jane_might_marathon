from fastapi import APIRouter, Depends, status, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from ..database import get_db
from ..services.lesson_service import LessonService
from ..schemas.lesson import LessonCreate, LessonResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()



templates = Jinja2Templates(directory = 'app/templates')


router = APIRouter(
    prefix='/lessons',
    tags=['lessons']
)


@router.get('', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def lessons(
    credentionals: Annotated[HTTPBasicCredentials, Depends(security)],
    request: Request,
    db: Session = Depends(get_db)
):
    if credentionals.username != 'admin' and credentionals.password != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'unauthorized'
        )
    service = LessonService(db)
    lessons = service.get_all_lessons()
    return templates.TemplateResponse('lessons.html', {'request': request, 'lessons': lessons})


@router.get('/create', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def create_user_form(
        request: Request,
        db: Session = Depends(get_db)
        ):
    return templates.TemplateResponse('create_lesson.html', {'request': request})


@router.post('/create', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: Annotated[LessonCreate, Form()],
    db:Session = Depends(get_db)
    ):
    user_service = LessonService(db)
    user_service.create(user_data)
    return RedirectResponse(url='/lessons', status_code=303)