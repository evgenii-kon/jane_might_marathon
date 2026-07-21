from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.novel_service import NovelService
from app.services.lesson_service import LessonService
from app.schemas.novel_line import NovelLineCreate, NovelLineUpdate, NOVEL_LINE_TYPES
from app.csrf import get_csrf_token

router = APIRouter(prefix="/admin/novel", tags=["admin_novel"])

CHARACTERS = ("confusi", "zhulan", "zhulan_waitress", "jo", "chingisu", "bris", "user")


@router.get("/", response_class=HTMLResponse)
async def list_lessons_with_novel(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Список уроков, у которых есть реплики новеллы"""
    novel_service = NovelService(db)
    lesson_service = LessonService(db)

    lesson_ids = await novel_service.get_lesson_ids_with_lines()
    lessons = await lesson_service.get_all_lessons()
    lessons_by_id = {lesson.id: lesson for lesson in lessons}

    rows = []
    for lesson_id in sorted(lesson_ids):
        lesson = lessons_by_id.get(lesson_id)
        if not lesson:
            continue
        lines = await novel_service.get_lines_by_lesson(lesson_id)
        rows.append({"lesson": lesson, "lines_count": len(lines)})

    return templates.TemplateResponse(
        "admin/novel/list.html",
        {"request": request, "rows": rows, "user": current_user},
    )


@router.get("/{lesson_id}", response_class=HTMLResponse)
async def lesson_lines(
    request: Request,
    lesson_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Список реплик урока с формами редактирования/добавления"""
    novel_service = NovelService(db)
    lesson_service = LessonService(db)

    lesson = await lesson_service.get_lesson_by_id(lesson_id)
    lines = await novel_service.get_lines_by_lesson(lesson_id)

    return templates.TemplateResponse(
        "admin/novel/lines.html",
        {
            "request": request,
            "lesson": lesson,
            "lines": lines,
            "characters": CHARACTERS,
            "line_types": NOVEL_LINE_TYPES,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{lesson_id}/create")
async def create_line(
    lesson_id: int,
    order: int = Form(0),
    type: str = Form(...),
    character: str = Form(""),
    speaker: str = Form(""),
    text: str = Form(...),
    side: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Добавить реплику урока"""
    novel_service = NovelService(db)
    data = NovelLineCreate(
        lesson_id=lesson_id,
        order=order,
        type=type,
        character=character or None,
        speaker=speaker or None,
        text=text,
        side=side or None,
    )
    await novel_service.create_line(data)
    return RedirectResponse(url=f"/admin/novel/{lesson_id}", status_code=303)


@router.post("/lines/{line_id}/update")
async def update_line(
    line_id: int,
    lesson_id: int = Form(...),
    order: int = Form(0),
    type: str = Form(...),
    character: str = Form(""),
    speaker: str = Form(""),
    text: str = Form(...),
    side: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Обновить реплику"""
    novel_service = NovelService(db)
    data = NovelLineUpdate(
        order=order,
        type=type,
        character=character or None,
        speaker=speaker or None,
        text=text,
        side=side or None,
    )
    await novel_service.update_line(line_id, data)
    return RedirectResponse(url=f"/admin/novel/{lesson_id}", status_code=303)


@router.post("/lines/{line_id}/delete")
async def delete_line(
    line_id: int,
    lesson_id: int = Form(...),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Удалить реплику"""
    novel_service = NovelService(db)
    await novel_service.delete_line(line_id)
    return RedirectResponse(url=f"/admin/novel/{lesson_id}", status_code=303)
