from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_admin
from app.models.user import User

from app.services.word_service import WordService
from app.services.lesson_service import LessonService
from app.schemas.word import WordCreate, WordUpdate
from app.csrf import get_csrf_token 


router = APIRouter(prefix="/admin/words", tags=["admin", "word"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_all_words(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    words = await word_service.get_all_words()
    return templates.TemplateResponse(
        "admin/words/words_list.html",
        {"request": request, "words": words, "user": current_admin}
    )


@router.get("/create", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def create_word_get(
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return templates.TemplateResponse(
        "admin/words/words_create.html",
        {
            "request": request, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def create_word_post(
    request: Request,
    word_data: Annotated[WordCreate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    await word_service.create_word(word_data)
    return RedirectResponse(url="/admin/words", status_code=status.HTTP_302_FOUND)


@router.get("/{word_id}/update", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def update_word_get(
    request: Request,
    word_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    word = await word_service.get_word_by_id(word_id)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word with id={word_id} not found",
        )
    return templates.TemplateResponse(
        "admin/words/words_edit.html",
        {
            "request": request, 
            "word": word, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{word_id}/update", status_code=status.HTTP_200_OK)
async def update_word_post(
    request: Request,
    word_id: int,
    word_data: Annotated[WordUpdate, Form()],
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    await word_service.update_word(word_id, word_data)
    return RedirectResponse(url="/admin/words", status_code=status.HTTP_302_FOUND)


@router.get("/{word_id}/delete", response_class=HTMLResponse)
async def delete_word_get(
    request: Request,
    word_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    word = await word_service.get_word_by_id(word_id)
    return templates.TemplateResponse(
        "admin/words/delete_word_confirm.html",
        {
            "request": request, 
            "word": word, 
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{word_id}/delete")
async def delete_word_post(
    word_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    await word_service.delete_word(word_id)
    return RedirectResponse(url="/admin/words", status_code=302)


@router.get("/{word_id}/lessons", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def manage_word_lessons(
    request: Request,
    word_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    word_service = WordService(db)
    lesson_service = LessonService(db)

    word = await word_service.get_word_by_id(word_id)
    all_lessons = await lesson_service.get_all_lessons()
    word_with_lessons = await word_service.get_word_with_lessons(word_id)
    existing_lesson_ids = set(word_with_lessons.lesson_ids)

    return templates.TemplateResponse(
        "admin/words/manage_lessons.html",
        {
            "request": request,
            "word": word,
            "lessons": all_lessons,
            "existing_lesson_ids": existing_lesson_ids,
            "user": current_admin,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{word_id}/lessons/add")
async def add_word_to_lesson(
    word_id: int,
    lesson_id: int = Form(...),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Добавить слово к уроку"""
    word_service = WordService(db)
    await word_service.add_word_to_lesson(word_id, lesson_id)
    return RedirectResponse(url=f"/admin/words/{word_id}/lessons", status_code=302)


@router.post("/{word_id}/lessons/remove")
async def remove_word_from_lesson(
    word_id: int,
    lesson_id: int = Form(...),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Удалить слово из урока"""
    word_service = WordService(db)
    await word_service.remove_word_from_lesson(word_id, lesson_id)
    return RedirectResponse(url=f"/admin/words/{word_id}/lessons", status_code=302)