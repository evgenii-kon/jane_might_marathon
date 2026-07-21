from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from app.templates_config import templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.csrf import get_csrf_token
from app.database import get_db
from app.dependencies.auth import get_current_user_optional, get_current_user
from app.dependencies.subscription import require_feature
from app.models.user import User
from app.services.idiom_service import IdiomService
from app.services.user_idiom_progress_service import UserIdiomProgressService

router = APIRouter(prefix="/idioms", tags=["public_idioms"])


@router.get("/", response_class=HTMLResponse)
async def list_idioms(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("idioms")),
):
    service = IdiomService(db)
    idioms = await service.get_all_idioms()

    progress_map: dict[int, str] = {}
    if current_user:
        from app.repositories.user_idiom_progress_repository import UserIdiomProgressRepository
        repo = UserIdiomProgressRepository(db)
        records = await repo.get_all_by_user(current_user.id)
        progress_map = {r.idiom_id: r.status for r in records}

    return templates.TemplateResponse(
        "idioms/list.html",
        {
            "request": request,
            "idioms": idioms,
            "user": current_user,
            "progress_map": progress_map,
        },
    )


@router.get("/{idiom_id}", response_class=HTMLResponse)
async def idiom_detail(
    request: Request,
    idiom_id: int,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("idioms")),
):
    service = IdiomService(db)
    idiom = await service.get_idiom_by_id(idiom_id)

    idiom_status = "not_known"
    if current_user:
        progress_service = UserIdiomProgressService(db)
        idiom_status = await progress_service.get_status(current_user.id, idiom_id)

    return templates.TemplateResponse(
        "idioms/detail.html",
        {
            "request": request,
            "idiom": idiom,
            "user": current_user,
            "idiom_status": idiom_status,
            "csrf_token": get_csrf_token(request),
        },
    )


class ProgressBody(BaseModel):
    status: str


@router.post("/{idiom_id}/progress", response_class=JSONResponse)
async def set_idiom_progress(
    idiom_id: int,
    body: ProgressBody,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_feature("idioms")),
):
    service = UserIdiomProgressService(db)
    new_status = await service.set_status(current_user.id, idiom_id, body.status)
    return {"status": new_status}
