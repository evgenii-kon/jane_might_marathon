from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from fastapi.templating import Jinja2Templates

from app.schemas.week import WeekCreate, WeekUpdate
from app.services.week_service import WeekService
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.csrf import get_csrf_token 


router = APIRouter(prefix="/admin/weeks", tags=["admin", "week"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_all_weeks(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    all_weeks = await week_service.get_all_weeks()
    return templates.TemplateResponse(
        "admin/weeks/weeks_list.html",
        {"request": request, "weeks": all_weeks, "user": current_admin}
    )


@router.get("/create", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def create_week_get(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return templates.TemplateResponse(
        "admin/weeks/weeks_create.html",
        {
            "request": request, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def create_week_post(
    request: Request,
    week_data: Annotated[WeekCreate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    await week_service.create_week(week_data)
    return RedirectResponse(url="/admin/weeks", status_code=status.HTTP_302_FOUND)


@router.get("/{week_id}/edit", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def update_week_get(
    request: Request,
    week_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    week = await week_service.get_week_by_id(week_id)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week with id={week_id} not found",
        )
    return templates.TemplateResponse(
        "admin/weeks/weeks_edit.html",
        {
            "request": request, 
            "week": week, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{week_id}/edit", status_code=status.HTTP_200_OK)
async def update_week_post(
    request: Request,
    week_id: int,
    week_data: Annotated[WeekUpdate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    await week_service.update_week(week_id, week_data)
    return RedirectResponse(url="/admin/weeks", status_code=status.HTTP_302_FOUND)


@router.get("/{week_id}/delete", response_class=HTMLResponse)
async def delete_week_get(
    request: Request,
    week_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    week = await week_service.get_week_by_id(week_id)
    return templates.TemplateResponse(
        "admin/weeks/delete_confirm.html",
        {
            "request": request, 
            "week": week, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{week_id}/delete")
async def delete_week_post(
    week_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    week_service = WeekService(db)
    await week_service.delete_week(week_id)
    return RedirectResponse(url="/admin/weeks", status_code=302)