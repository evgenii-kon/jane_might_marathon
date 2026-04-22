from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from ..database import get_db
from ..services.user_service import UserService
from ..schemas.user import UserCreate, UserResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form

""" user update и create будет в auth """

templates = Jinja2Templates(directory = 'app/templates')

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get('', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_users(request: Request,
              db: Session = Depends(get_db)
              ):
    service = UserService(db)
    users = service.get_all_users()
    return templates.TemplateResponse('users.html', {'request': request, 'users': users})


@router.get('/create', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def create_user(
    request: Request,
    db:Session = Depends(get_db)
    ):
    return templates.TemplateResponse('create_user.html', {'request': request})


@router.post('/create', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: Annotated[UserCreate, Form()],
    db:Session = Depends(get_db)
    ):
    user_service = UserService(db)
    user_service.create_user(user_data)
    return RedirectResponse(url='/users', status_code=303)