from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Annotated
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi import Form, HTTPException

from app.models.week import Week
from app.schemas.week import WeekCreate, WeekResponse, WeekUpdate
from app.repositories.week_repository import WeekRepository
from app.services.week_service import WeekService
from app.dependencies.auth import get_current_admin
from app.models.user import User


router = APIRouter(prefix='/admin/weeks', tags=['admin', 'week'])

templates = Jinja2Templates(directory='app/templates')


@router.get('/all_weeks', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_weeks(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    week_service = WeekService(db)
    all_weeks = week_service.get_all_weeks()
    return templates.TemplateResponse('all_weeks.html', {"request": request, 'all_weeks': all_weeks})


@router.get('/create', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def create_week_get(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse('create_week.html', {'request': request})


@router.post('/create', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_week_post(
    request: Request,
    week_data: Annotated[WeekCreate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    week_service = WeekService(db)
    week = week_service.create_week(week_data)
    return RedirectResponse(url='/admin/weeks/all_weeks', status_code=status.HTTP_302_FOUND)


@router.get('/{week_id}/update', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def update_week_get(
    request: Request,
    week_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    week_service = WeekService(db)
    week = week_service.get_week_by_id(week_id)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Week with id={week_id} not found'
        )
    return templates.TemplateResponse('update_week.html', {'request': request, 'week': week})


@router.post('/{week_id}/update', status_code=status.HTTP_200_OK)
def update_week_post(
    request: Request,
    week_id: int,
    week_data: Annotated[WeekUpdate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    week_service = WeekService(db)
    week = week_service.update_week(week_id, week_data)
    return RedirectResponse('/admin/weeks/all_weeks', status_code=status.HTTP_302_FOUND)


@router.get('/{week_id}/delete', response_class=HTMLResponse)
def delete_week_get(
    request: Request,
    week_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    week_service = WeekService(db)
    week = week_service.get_week_by_id(week_id)
    return templates.TemplateResponse('delete_week_confirm.html', {'request': request, 'week': week})


@router.post('/{week_id}/delete')
def delete_week_post(
    week_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    WeekService(db).delete_week(week_id)
    return RedirectResponse(url='/admin/weeks/all_weeks', status_code=302)