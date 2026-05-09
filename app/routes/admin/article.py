from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.article_service import ArticleService
from app.schemas.article import ArticleCreate, ArticleUpdate

router = APIRouter(prefix='/admin/articles', tags=['admin_articles'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
def list_articles(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Список статей"""
    service = ArticleService(db)
    articles = service.get_all_articles()
    
    return templates.TemplateResponse('admin/articles/articles_list.html', {
        'request': request,
        'articles': articles,
        'user': current_user
    })


@router.get('/create', response_class=HTMLResponse)
def create_article_form(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Форма создания статьи"""
    return templates.TemplateResponse('admin/articles/articles_create.html', {
        'request': request,
        'user': current_user
    })


@router.post('/create')
def create_article(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    images: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Создание статьи"""
    service = ArticleService(db)
    
    # Преобразуем строку с изображениями в список
    images_list = [img.strip() for img in images.split(',') if img.strip()]
    
    try:
        article_data = ArticleCreate(
            name=name,
            slug=slug,
            description=description,
            text=text,
            images=images_list
        )
        service.create_article(article_data)
        return RedirectResponse(url='/admin/articles', status_code=303)
    
    except Exception as e:
        return templates.TemplateResponse('admin/articles/articles_create.html', {
            'request': request,
            'error': str(e),
            'form_data': {
                'name': name,
                'slug': slug,
                'description': description,
                'text': text,
                'images': images
            },
            'user': current_user
        })


@router.get('/{article_id}/edit', response_class=HTMLResponse)
def edit_article_form(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Форма редактирования статьи"""
    service = ArticleService(db)
    article = service.get_article_by_id(article_id)
    
    # Преобразуем список изображений в строку для формы
    images_str = ','.join(article.images) if article.images else ''
    
    return templates.TemplateResponse('admin/articles/articles_edit.html', {
        'request': request,
        'article': article,
        'images_str': images_str,
        'user': current_user
    })


@router.post('/{article_id}/edit')
def edit_article(
    request: Request,
    article_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    images: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Обновление статьи"""
    service = ArticleService(db)
    
    # Преобразуем строку с изображениями в список
    images_list = [img.strip() for img in images.split(',') if img.strip()]
    
    try:
        article_data = ArticleUpdate(
            name=name,
            slug=slug,
            description=description,
            text=text,
            images=images_list
        )
        service.update_article(article_id, article_data)
        return RedirectResponse(url='/admin/articles', status_code=303)
    
    except Exception as e:
        article = service.get_article_by_id(article_id)
        return templates.TemplateResponse('admin/articles/articles_edit.html', {
            'request': request,
            'article': article,
            'error': str(e),
            'form_data': {
                'name': name,
                'slug': slug,
                'description': description,
                'text': text,
                'images': images
            },
            'user': current_user
        })


@router.get('/{article_id}/delete', response_class=HTMLResponse)
def delete_article_confirm(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Подтверждение удаления статьи"""
    service = ArticleService(db)
    article = service.get_article_by_id(article_id)
    
    return templates.TemplateResponse('admin/articles/delete_confirm.html', {
        'request': request,
        'article': article,
        'user': current_user
    })


@router.post('/{article_id}/delete')
def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Удаление статьи"""
    service = ArticleService(db)
    service.delete_article(article_id)
    
    return RedirectResponse(url='/admin/articles', status_code=303)