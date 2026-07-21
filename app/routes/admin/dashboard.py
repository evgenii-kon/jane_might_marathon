from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: User = Depends(get_current_admin)):
    """
    Главная страница админ-панели
    """
    return templates.TemplateResponse(
        "admin/dashboard.html", {"request": request, "admin": admin}
    )
