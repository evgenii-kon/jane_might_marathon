from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix='/admin', tags=['admin'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    admin: User = Depends(get_current_admin)
):
    """
    Главная страница админ-панели
    """
    return templates.TemplateResponse('admin/dashboard.html', {
        'request': request,
        'admin': admin
    })