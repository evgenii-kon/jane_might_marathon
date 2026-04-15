from fastapi import FastAPI, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .routes.user import router as user_router
from .routes.lesson import router as lesson_router
from .database import init_db
from .models.user import User
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.get_env('SECRET_KEY')
ALGORITHM = os.get_env('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.get_env('ACCESS_TOKEN_EXPIRE_MINUTES')


init_db()

app = FastAPI()

app.include_router(user_router)
app.include_router(lesson_router)

templates = Jinja2Templates('app/templates')

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get('/',response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

