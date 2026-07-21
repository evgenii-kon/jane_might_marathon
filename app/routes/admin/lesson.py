from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.templates_config import templates
from app.dependencies.auth import get_current_admin
from app.models.user import User

from app.schemas.lesson import LessonCreate, LessonUpdate
from app.services.lesson_service import LessonService

router = APIRouter(prefix="/admin/lessons", tags=["admin", "lesson"])
from app.csrf import get_csrf_token 



@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_all_lessons(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    all_lessons = await lesson_service.get_all_lessons()
    return templates.TemplateResponse(
        "admin/lessons/lessons_list.html",
        {"request": request, "lessons": all_lessons, "user": current_admin}
    )


@router.get("/create", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def create_lesson_get(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return templates.TemplateResponse(
        "admin/lessons/lesson_create.html", {
            "request": request, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson_post(
    request: Request,
    lesson_data: Annotated[LessonCreate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    await lesson_service.create_lesson(lesson_data)
    return RedirectResponse(url="/admin/lessons", status_code=302)


@router.get("/{lesson_id}/edit", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def update_lesson_get(
    request: Request,
    lesson_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    lesson = await lesson_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"lesson with id = {lesson_id} not found",
        )
    return templates.TemplateResponse(
        "admin/lessons/lesson_edit.html",
        {
            "request": request, 
            "lesson": lesson, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{lesson_id}/edit", status_code=status.HTTP_200_OK)
async def update_lesson_post(
    request: Request,
    lesson_id: int,
    lesson_data: Annotated[LessonUpdate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    await lesson_service.update_lesson(lesson_id, lesson_data)
    return RedirectResponse(url="/admin/lessons", status_code=302)


@router.get("/{lesson_id}/delete", response_class=HTMLResponse)
async def delete_lesson_get(
    request: Request,
    lesson_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    lesson = await lesson_service.get_lesson_by_id(lesson_id)
    return templates.TemplateResponse(
        "admin/lessons/delete_confirm.html",
        {
            "request": request, 
            "lesson": lesson, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{lesson_id}/delete")
async def delete_lesson_post(
    lesson_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    lesson_service = LessonService(db)
    await lesson_service.delete_lesson(lesson_id)
    return RedirectResponse(url="/admin/lessons", status_code=302)