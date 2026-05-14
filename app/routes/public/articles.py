from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user_optional
from app.models.user import User
from app.services.article_service import ArticleService

router = APIRouter(prefix='/articles', tags=['public_articles'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
def list_articles(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Список всех статей"""
    service = ArticleService(db)
    articles = service.get_all_articles()
    
    return templates.TemplateResponse('public/articles/list.html', {
        'request': request,
        'articles': articles,
        'user': current_user
    })


@router.get('/{slug}', response_class=HTMLResponse)
def article_detail(
    request: Request,
    slug: str,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Детальная страница статьи"""
    service = ArticleService(db)
    
    try:
        article = service.get_article_by_slug(slug)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return templates.TemplateResponse('public/articles/detail.html', {
        'request': request,
        'article': article,
        'user': current_user
    })