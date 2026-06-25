from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_optional
from app.models.user import User
from app.services.grammar_rule_service import GrammarRuleService
from app.services.grammar_tag_service import GrammarTagService

router = APIRouter(prefix="/grammar", tags=["public_grammar"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_grammar_rules(
    request: Request,
    tag: str = None,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    rule_service = GrammarRuleService(db)
    tag_service = GrammarTagService(db)

    tags = await tag_service.get_all_tags()
    rules = await rule_service.get_rules_by_tag(tag) if tag else await rule_service.get_all_rules()

    return templates.TemplateResponse(
        "grammar/list.html",
        {
            "request": request,
            "rules": rules,
            "tags": tags,
            "active_tag": tag,
            "user": current_user,
        },
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def grammar_rule_detail(
    request: Request,
    slug: str,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    service = GrammarRuleService(db)
    try:
        rule = await service.get_rule_by_slug(slug)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Grammar rule not found")

    return templates.TemplateResponse(
        "grammar/detail.html",
        {"request": request, "rule": rule, "user": current_user},
    )
