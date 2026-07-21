from fastapi.templating import Jinja2Templates

from app.config import settings
from app.csrf import get_csrf_token

templates = Jinja2Templates("app/templates")
templates.env.globals["s3_public_url"] = settings.S3_PUBLIC_URL
templates.env.globals["csrf"] = get_csrf_token
