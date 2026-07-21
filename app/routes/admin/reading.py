from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.reading_text_service import ReadingTextService
from app.repositories.reading_question_repository import ReadingQuestionRepository
from app.schemas.reading import ReadingTextCreate, ReadingTextUpdate, ReadingQuestionCreate
from app.csrf import get_csrf_token

router = APIRouter(prefix="/admin/reading", tags=["admin_reading"])


@router.get("/", response_class=HTMLResponse)
async def list_texts(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ReadingTextService(db)
    texts = await service.get_all()
    return templates.TemplateResponse(
        "admin/reading/list.html",
        {"request": request, "texts": texts, "user": current_user},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_form(
    request: Request,
    current_user: User = Depends(get_current_admin),
):
    return templates.TemplateResponse(
        "admin/reading/form.html",
        {"request": request, "user": current_user, "csrf_token": get_csrf_token(request), "text": None},
    )


@router.post("/create")
async def create_text(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    content_hanzi: str = Form(...),
    content_pinyin: str = Form(""),
    content_translation: str = Form(""),
    hsk_level: str = Form(""),
    week_id: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ReadingTextService(db)
    try:
        data = ReadingTextCreate(
            title=title,
            slug=slug,
            description=description or None,
            content_hanzi=content_hanzi,
            content_pinyin=content_pinyin or None,
            content_translation=content_translation or None,
            hsk_level=hsk_level or None,
            week_id=int(week_id) if week_id.strip() else None,
        )
        created = await service.create(data)
        return RedirectResponse(url=f"/admin/reading/{created.id}/edit", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "admin/reading/form.html",
            {
                "request": request,
                "user": current_user,
                "csrf_token": get_csrf_token(request),
                "text": None,
                "error": str(e),
                "form_data": {
                    "title": title, "slug": slug, "description": description,
                    "content_hanzi": content_hanzi, "content_pinyin": content_pinyin,
                    "content_translation": content_translation, "hsk_level": hsk_level,
                },
            },
        )


@router.get("/{text_id}/edit", response_class=HTMLResponse)
async def edit_form(
    request: Request,
    text_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ReadingTextService(db)
    text = await service.get_by_id(text_id)
    q_repo = ReadingQuestionRepository(db)
    questions = await q_repo.get_by_text_id(text_id)
    return templates.TemplateResponse(
        "admin/reading/form.html",
        {
            "request": request,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
            "text": text,
            "questions": questions,
        },
    )


@router.post("/{text_id}/edit")
async def edit_text(
    request: Request,
    text_id: int,
    title: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    content_hanzi: str = Form(...),
    content_pinyin: str = Form(""),
    content_translation: str = Form(""),
    hsk_level: str = Form(""),
    week_id: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ReadingTextService(db)
    try:
        data = ReadingTextUpdate(
            title=title,
            slug=slug,
            description=description or None,
            content_hanzi=content_hanzi,
            content_pinyin=content_pinyin or None,
            content_translation=content_translation or None,
            hsk_level=hsk_level or None,
            week_id=int(week_id) if week_id.strip() else None,
        )
        await service.update(text_id, data)
        return RedirectResponse(url=f"/admin/reading/{text_id}/edit", status_code=303)
    except Exception as e:
        text = await service.get_by_id(text_id)
        q_repo = ReadingQuestionRepository(db)
        questions = await q_repo.get_by_text_id(text_id)
        return templates.TemplateResponse(
            "admin/reading/form.html",
            {
                "request": request,
                "user": current_user,
                "csrf_token": get_csrf_token(request),
                "text": text,
                "questions": questions,
                "error": str(e),
            },
        )


@router.post("/{text_id}/delete")
async def delete_text(
    text_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ReadingTextService(db)
    await service.delete(text_id)
    return RedirectResponse(url="/admin/reading", status_code=303)


# --- Question management ---

@router.post("/{text_id}/questions/add")
async def add_question(
    request: Request,
    text_id: int,
    question: str = Form(...),
    option_1: str = Form(...),
    option_2: str = Form(...),
    option_3: str = Form(...),
    option_4: str = Form(...),
    correct_answer: int = Form(...),
    explanation: str = Form(""),
    order_in_text: int = Form(0),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    q_repo = ReadingQuestionRepository(db)
    data = ReadingQuestionCreate(
        question=question,
        option_1=option_1,
        option_2=option_2,
        option_3=option_3,
        option_4=option_4,
        correct_answer=correct_answer,
        explanation=explanation or None,
        order_in_text=order_in_text,
    )
    await q_repo.create(text_id, data)
    return RedirectResponse(url=f"/admin/reading/{text_id}/edit", status_code=303)


@router.post("/{text_id}/questions/{question_id}/delete")
async def delete_question(
    text_id: int,
    question_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    q_repo = ReadingQuestionRepository(db)
    await q_repo.delete(question_id)
    return RedirectResponse(url=f"/admin/reading/{text_id}/edit", status_code=303)
