from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.idiom_service import IdiomService
from app.schemas.idiom import IdiomCreate, IdiomUpdate
from app.csrf import get_csrf_token

router = APIRouter(prefix="/admin/idioms", tags=["admin_idioms"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_idioms(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = IdiomService(db)
    idioms = await service.get_all_idioms()
    return templates.TemplateResponse(
        "admin/idioms/list.html",
        {"request": request, "idioms": idioms, "user": current_user},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_idiom_form(
    request: Request,
    current_user: User = Depends(get_current_admin),
):
    return templates.TemplateResponse(
        "admin/idioms/form.html",
        {
            "request": request,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/create")
async def create_idiom(
    request: Request,
    hanzi: str = Form(...),
    pinyin: str = Form(...),
    translate: str = Form(...),
    meaning: str = Form(...),
    story: Optional[str] = Form(None),
    example: Optional[str] = Form(None),
    example_translation: Optional[str] = Form(None),
    audio_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = IdiomService(db)

    def empty_to_none(v: Optional[str]) -> Optional[str]:
        return v.strip() if v and v.strip() else None

    try:
        idiom_data = IdiomCreate(
            hanzi=hanzi,
            pinyin=pinyin,
            translate=translate,
            meaning=meaning,
            story=empty_to_none(story),
            example=empty_to_none(example),
            example_translation=empty_to_none(example_translation),
            audio_url=empty_to_none(audio_url),
        )
        await service.create_idiom(idiom_data)
        return RedirectResponse(url="/admin/idioms", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "admin/idioms/form.html",
            {
                "request": request,
                "error": str(e),
                "form_data": {
                    "hanzi": hanzi,
                    "pinyin": pinyin,
                    "translate": translate,
                    "meaning": meaning,
                    "story": story,
                    "example": example,
                    "example_translation": example_translation,
                    "audio_url": audio_url,
                },
                "user": current_user,
                "csrf_token": get_csrf_token(request),
            },
        )


@router.get("/{idiom_id}/edit", response_class=HTMLResponse)
async def edit_idiom_form(
    request: Request,
    idiom_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = IdiomService(db)
    idiom = await service.get_idiom_by_id(idiom_id)
    return templates.TemplateResponse(
        "admin/idioms/form.html",
        {
            "request": request,
            "idiom": idiom,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{idiom_id}/edit")
async def edit_idiom(
    request: Request,
    idiom_id: int,
    hanzi: str = Form(...),
    pinyin: str = Form(...),
    translate: str = Form(...),
    meaning: str = Form(...),
    story: Optional[str] = Form(None),
    example: Optional[str] = Form(None),
    example_translation: Optional[str] = Form(None),
    audio_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = IdiomService(db)

    def empty_to_none(v: Optional[str]) -> Optional[str]:
        return v.strip() if v and v.strip() else None

    try:
        idiom_data = IdiomUpdate(
            hanzi=hanzi,
            pinyin=pinyin,
            translate=translate,
            meaning=meaning,
            story=empty_to_none(story),
            example=empty_to_none(example),
            example_translation=empty_to_none(example_translation),
            audio_url=empty_to_none(audio_url),
        )
        await service.update_idiom(idiom_id, idiom_data)
        return RedirectResponse(url="/admin/idioms", status_code=303)
    except Exception as e:
        try:
            idiom = await service.get_idiom_by_id(idiom_id)
        except Exception:
            idiom = None
        return templates.TemplateResponse(
            "admin/idioms/form.html",
            {
                "request": request,
                "idiom": idiom,
                "error": str(e),
                "form_data": {
                    "hanzi": hanzi,
                    "pinyin": pinyin,
                    "translate": translate,
                    "meaning": meaning,
                    "story": story,
                    "example": example,
                    "example_translation": example_translation,
                    "audio_url": audio_url,
                },
                "user": current_user,
                "csrf_token": get_csrf_token(request),
            },
        )


@router.post("/{idiom_id}/delete")
async def delete_idiom(
    idiom_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = IdiomService(db)
    await service.delete_idiom(idiom_id)
    return RedirectResponse(url="/admin/idioms", status_code=303)
