from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.grammar_rule_service import GrammarRuleService
from app.services.grammar_tag_service import GrammarTagService
from app.schemas.grammar import GrammarRuleCreate, GrammarRuleUpdate
from app.csrf import get_csrf_token

router = APIRouter(prefix="/admin/grammar", tags=["admin_grammar"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_grammar_rules(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GrammarRuleService(db)
    rules = await service.get_all_rules()
    return templates.TemplateResponse(
        "admin/grammar/list.html",
        {"request": request, "rules": rules, "user": current_user, "csrf_token": get_csrf_token(request)},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_grammar_rule_form(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    tag_service = GrammarTagService(db)
    tags = await tag_service.get_all_tags()
    return templates.TemplateResponse(
        "admin/grammar/form.html",
        {
            "request": request,
            "user": current_user,
            "tags": tags,
            "rule": None,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/create")
async def create_grammar_rule(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    title = form.get("title", "")
    slug = form.get("slug", "")
    description = form.get("description", "") or None
    content = form.get("content", "")
    hsk_level = form.get("hsk_level", "") or None
    tag_ids = [int(x) for x in form.getlist("tag_ids") if x]

    service = GrammarRuleService(db)
    tag_service = GrammarTagService(db)

    try:
        data = GrammarRuleCreate(
            title=title,
            slug=slug,
            description=description,
            content=content,
            hsk_level=hsk_level,
            tag_ids=tag_ids,
        )
        await service.create_rule(data)
        return RedirectResponse(url="/admin/grammar", status_code=303)
    except Exception as e:
        tags = await tag_service.get_all_tags()
        return templates.TemplateResponse(
            "admin/grammar/form.html",
            {
                "request": request,
                "error": str(e),
                "tags": tags,
                "rule": None,
                "form_data": {
                    "title": title,
                    "slug": slug,
                    "description": description or "",
                    "content": content,
                    "hsk_level": hsk_level or "",
                    "tag_ids": tag_ids,
                },
                "user": current_user,
                "csrf_token": get_csrf_token(request),
            },
        )


@router.get("/{rule_id}/edit", response_class=HTMLResponse)
async def edit_grammar_rule_form(
    request: Request,
    rule_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GrammarRuleService(db)
    tag_service = GrammarTagService(db)
    rule = await service.get_rule_by_id(rule_id)
    tags = await tag_service.get_all_tags()
    return templates.TemplateResponse(
        "admin/grammar/form.html",
        {
            "request": request,
            "rule": rule,
            "tags": tags,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{rule_id}/edit")
async def edit_grammar_rule(
    request: Request,
    rule_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    title = form.get("title", "")
    slug = form.get("slug", "")
    description = form.get("description", "") or None
    content = form.get("content", "")
    hsk_level = form.get("hsk_level", "") or None
    tag_ids = [int(x) for x in form.getlist("tag_ids") if x]

    service = GrammarRuleService(db)
    tag_service = GrammarTagService(db)

    try:
        data = GrammarRuleUpdate(
            title=title,
            slug=slug,
            description=description,
            content=content,
            hsk_level=hsk_level,
            tag_ids=tag_ids,
        )
        await service.update_rule(rule_id, data)
        return RedirectResponse(url="/admin/grammar", status_code=303)
    except Exception as e:
        try:
            rule = await service.get_rule_by_id(rule_id)
        except Exception:
            rule = None
        tags = await tag_service.get_all_tags()
        return templates.TemplateResponse(
            "admin/grammar/form.html",
            {
                "request": request,
                "error": str(e),
                "rule": rule,
                "tags": tags,
                "form_data": {
                    "title": title,
                    "slug": slug,
                    "description": description or "",
                    "content": content,
                    "hsk_level": hsk_level or "",
                    "tag_ids": tag_ids,
                },
                "user": current_user,
                "csrf_token": get_csrf_token(request),
            },
        )


@router.post("/{rule_id}/delete")
async def delete_grammar_rule(
    rule_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GrammarRuleService(db)
    await service.delete_rule(rule_id)
    return RedirectResponse(url="/admin/grammar", status_code=303)
