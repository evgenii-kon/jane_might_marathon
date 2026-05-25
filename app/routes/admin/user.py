from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin/users", tags=["admin", "users"])
templates = Jinja2Templates(directory="app/templates")
from app.csrf import get_csrf_token 



# ============ СПИСОК ПОЛЬЗОВАТЕЛЕЙ ============


@router.get("/", response_class=HTMLResponse)
async def list_users(
    request: Request,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Список всех пользователей (только для админа)"""
    user_service = UserService(db)
    users = await user_service.get_all_users()

    return templates.TemplateResponse(
        "admin/users/users_list.html",
        {"request": request, "users": users, "admin": admin},
    )


# ============ СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ ============


@router.get("/create", response_class=HTMLResponse)
async def create_user_form(
    request: Request,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Форма создания пользователя"""
    return templates.TemplateResponse(
        "admin/users/user_create.html", {
            "request": request, 
            "admin": admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    telegram: Optional[str] = Form(None),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Создание пользователя (админ)"""
    user_service = UserService(db)

    try:
        user_data = UserCreate(
            name=name, email=email, password=password, telegram=telegram
        )
        await user_service.create_user(user_data)
        return RedirectResponse(url="/admin/users", status_code=302)
    except HTTPException as e:
        return templates.TemplateResponse(
            "admin/users/user_create.html",
            {
                "request": request, 
                "error": e.detail, "admin": admin,
                "csrf_token": get_csrf_token(request),
                }
        )


# ============ РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ ============


@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Форма редактирования пользователя (админ)"""
    user_service = UserService(db)

    try:
        user = await user_service.get_user_by_id(user_id)
        return templates.TemplateResponse(
            "admin/users/users_edit.html",
            {
                "request": request, 
                "user": user, 
                "admin": admin,
                "csrf_token": get_csrf_token(request),
                }
        )
    except HTTPException:
        return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user(
    request: Request,
    user_id: int,
    name: str = Form(...),
    email: str = Form(...),
    telegram: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Обновление пользователя (админ)"""
    user_service = UserService(db)

    try:
        update_data = UserUpdate(
            name=name,
            email=email,
            telegram=telegram,
            password=password if password else None,
        )
        await user_service.update_user(user_id, update_data)
        return RedirectResponse(url="/admin/users", status_code=302)
    except HTTPException as e:
        user = await user_service.get_user_by_id(user_id)
        return templates.TemplateResponse(
            "admin/users/users_edit.html",
            {
                "request": request, 
                "user": user, 
                "error": e.detail, 
                "admin": admin,
                "csrf_token": get_csrf_token(request),
                },
        )


# ============ УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ============


@router.get("/{user_id}/delete", response_class=HTMLResponse)
async def delete_user_form(
    request: Request,
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Форма подтверждения удаления пользователя"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    return templates.TemplateResponse(
        "admin/users/delete.html",
        {
            "request": request, 
            "user": user, 
            "admin": admin,
            "csrf_token": get_csrf_token(request),
            }
    )


@router.post("/{user_id}/delete")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Удаление пользователя (админ)"""
    user_service = UserService(db)
    await user_service.delete_user(user_id)
    return RedirectResponse(url="/admin/users", status_code=302)