from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_optional
from app.models.user import User
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["public_articles"])


@router.get("/", response_class=HTMLResponse)
async def list_articles(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Список всех статей"""
    service = ArticleService(db)
    articles =await service.get_all_articles()

    return templates.TemplateResponse(
        "public/articles/list.html",
        {"request": request, "articles": articles, "user": current_user},
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def article_detail(
    request: Request,
    slug: str,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Детальная страница статьи"""
    service = ArticleService(db)

    try:
        article = await service.get_article_by_slug(slug)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Article not found")

    return templates.TemplateResponse(
        "public/articles/detail.html",
        {"request": request, "article": article, "user": current_user},
    )
