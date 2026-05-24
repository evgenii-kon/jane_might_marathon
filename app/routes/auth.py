from fastapi import APIRouter, Depends, status, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_week_progress_service import UserWeekProgressService
from app.dependencies.auth import get_current_user_optional, get_current_user
from app.models.user import User
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


# ============ РЕГИСТРАЦИЯ ============


@router.get("/register", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def register_get(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "user": current_user}
    )


@router.post("/register", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def register_post(
    user_data: Annotated[UserCreate, Form()],
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    user_service = UserService(db)
    week_progress_service = UserWeekProgressService(db)

    try:
        new_user = await user_service.create_user(user_data)
        await week_progress_service.init_user_weeks(new_user.id)

        return RedirectResponse(url="/auth/login", status_code=302)
    except HTTPException as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": e.detail, "user": current_user},
        )


# ============ ЛОГИН ============


@router.get("/login", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def login_get(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "user": current_user}
    )


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    user_service = UserService(db)

    try:
        user = await user_service.authenticate_user(email, password)
        access_token = create_access_token(data={"user_id": user.id})

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
        )
        return response

    except HTTPException:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Invalid email or password",
                "user": current_user,
            },
        )


# ============ ВЫХОД ============


@router.get("/logout", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def logout_get(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth/logout.html", {"request": request, "user": current_user}
    )


@router.post("/logout")
async def logout_post():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


# ============ ПРОФИЛЬ ============


@router.get("/me", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.lesson_service import LessonService
    from app.services.user_lesson_progress_service import UserLessonProgressService

    lesson_service = LessonService(db)
    progress_service = UserLessonProgressService(db)

    total_lessons = await lesson_service.get_lessons_count()
    completed_lessons = await progress_service.get_completed_count_by_user(current_user.id)
    progress_percent = (
        int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    )

    return templates.TemplateResponse(
        "auth/user_data.html",
        {
            "request": request,
            "user": current_user,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percent": progress_percent,
        },
    )


@router.get("/me/edit", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def edit_profile_get(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "auth/user_edit_form.html", {"request": request, "user": current_user}
    )


@router.post("/me/edit", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def edit_profile_post(
    request: Request,
    user_data: Annotated[UserUpdate, Form()],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service = UserService(db)
    try:
        await user_service.update_user(current_user.id, user_data)
        return RedirectResponse(url="/auth/me", status_code=302)
    except HTTPException as e:
        return templates.TemplateResponse(
            "auth/user_edit_form.html",
            {"request": request, "user": current_user, "error": e.detail},
        )


# ============ УДАЛЕНИЕ АККАУНТА ============


@router.get("/me/delete", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def delete_account_get(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "auth/delete_user_confirm.html", {"request": request, "user": current_user}
    )


@router.post("/me/delete")
async def delete_account_post(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.delete_user(current_user.id)

    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response