from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.article_service import ArticleService
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.csrf import get_csrf_token 


router = APIRouter(prefix="/admin/articles", tags=["admin_articles"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_articles(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    articles = await service.get_all_articles()
    return templates.TemplateResponse(
        "admin/articles/articles_list.html",
        {"request": request, "articles": articles, "user": current_user},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_article_form(
    request: Request,
    current_user: User = Depends(get_current_admin),
):
    return templates.TemplateResponse(
        "admin/articles/articles_create.html",
        {
            "request": request, 
            "user": current_user,
            "csrf_token": get_csrf_token(request),
            },
    )


@router.post("/create")
async def create_article(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    images: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    images_list = [img.strip() for img in images.split(",") if img.strip()]

    try:
        article_data = ArticleCreate(
            name=name, slug=slug, description=description, text=text, images=images_list
        )
        await service.create_article(article_data)
        return RedirectResponse(url="/admin/articles", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "admin/articles/articles_create.html",
            {
                "request": request,
                "error": str(e),
                "form_data": {
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "text": text,
                    "images": images,
                },
                "user": current_user,
                "csrf_token": get_csrf_token(request)
            },
        )


@router.get("/{article_id}/edit", response_class=HTMLResponse)
async def edit_article_form(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.get_article_by_id(article_id)
    images_str = ",".join(article.images) if article.images else ""
    return templates.TemplateResponse(
        "admin/articles/articles_edit.html",
        {
            "request": request,
            "article": article,
            "images_str": images_str,
            "user": current_user,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/{article_id}/edit")
async def edit_article(
    request: Request,
    article_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    images: str = Form(""),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    images_list = [img.strip() for img in images.split(",") if img.strip()]

    try:
        article_data = ArticleUpdate(
            name=name, slug=slug, description=description, text=text, images=images_list
        )
        await service.update_article(article_id, article_data)
        return RedirectResponse(url="/admin/articles", status_code=303)
    except Exception as e:
        try:
            article = await service.get_article_by_id(article_id)
        except:
            article = None
        return templates.TemplateResponse(
            "admin/articles/articles_edit.html",
            {
                "request": request,
                "article": article,
                "error": str(e),
                "form_data": {
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "text": text,
                    "images": images,
                },
                "user": current_user,
                "csrf_token": get_csrf_token(request)
            },
        )


@router.get("/{article_id}/delete", response_class=HTMLResponse)
async def delete_article_confirm(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.get_article_by_id(article_id)
    return templates.TemplateResponse(
        "admin/articles/delete_confirm.html",
        {
            "request": request,
            "article": article, 
            "user": current_user,
            "csrf_token": get_csrf_token(request),
            },
    )


@router.post("/{article_id}/delete")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    await service.delete_article(article_id)
    return RedirectResponse(url="/admin/articles", status_code=303)