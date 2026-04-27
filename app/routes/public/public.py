from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=['public'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
