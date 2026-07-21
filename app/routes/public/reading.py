from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_optional
from app.dependencies.subscription import require_feature
from app.models.user import User
from app.services.reading_text_service import ReadingTextService
from app.repositories.user_reading_progress_repository import UserReadingProgressRepository
from app.csrf import get_csrf_token

router = APIRouter(prefix="/reading", tags=["public_reading"])


@router.get("/", response_class=HTMLResponse)
async def list_reading_texts(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("reading")),
):
    service = ReadingTextService(db)
    texts = await service.get_all()

    completed_ids = set()
    if current_user:
        progress_repo = UserReadingProgressRepository(db)
        completed_ids = await progress_repo.get_completed_ids(current_user.id)

    return templates.TemplateResponse(
        "reading/list.html",
        {"request": request, "texts": texts, "user": current_user, "completed_ids": completed_ids},
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def reading_detail(
    request: Request,
    slug: str,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("reading")),
):
    service = ReadingTextService(db)
    try:
        text = await service.get_by_slug(slug)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Текст не найден")

    is_completed = False
    if current_user:
        progress_repo = UserReadingProgressRepository(db)
        progress = await progress_repo.get(current_user.id, text.id)
        is_completed = progress.is_completed if progress else False

    return templates.TemplateResponse(
        "reading/detail.html",
        {
            "request": request,
            "text": text,
            "user": current_user,
            "is_completed": is_completed,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{slug}/check")
async def check_answers(
    request: Request,
    slug: str,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("reading")),
):
    service = ReadingTextService(db)
    try:
        text = await service.get_by_slug(slug)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Текст не найден")

    form = await request.form()
    results = []

    for q in text.questions:
        raw = form.get(f"q_{q.id}")
        selected = int(raw) if raw and raw.isdigit() else None
        is_correct = selected == q.correct_answer
        results.append({
            "question_id": q.id,
            "question": q.question,
            "selected": selected,
            "correct": is_correct,
            "correct_answer": q.correct_answer,
            "option_1": q.option_1,
            "option_2": q.option_2,
            "option_3": q.option_3,
            "option_4": q.option_4,
            "explanation": q.explanation,
        })

    if current_user:
        progress_repo = UserReadingProgressRepository(db)
        await progress_repo.mark_completed(current_user.id, text.id)

    return templates.TemplateResponse(
        "reading/detail.html",
        {
            "request": request,
            "text": text,
            "user": current_user,
            "is_completed": True,
            "check_results": results,
            "csrf_token": get_csrf_token(request),
        },
    )
