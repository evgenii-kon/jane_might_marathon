from fastapi import APIRouter, Depends, status, Request
from typing import Optional
from app.models.user import User
from app.dependencies.auth import get_current_user_optional
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def index(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user}
    )


@router.get("/about", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def about(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "public/about.html", {"request": request, "user": current_user}
    )
