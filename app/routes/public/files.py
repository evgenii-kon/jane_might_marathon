import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templates_config import templates

from app.dependencies.auth import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/files", tags=["public_files"])

FILES_DIR = "app/static/files"

EXTENSION_LABELS = {
    ".pdf": "PDF",
    ".doc": "DOC",
    ".docx": "DOCX",
    ".zip": "ZIP",
    ".mp3": "MP3",
    ".png": "PNG",
    ".jpg": "JPG",
    ".jpeg": "JPG",
}


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "Б" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ТБ"


def _list_files() -> list:
    if not os.path.isdir(FILES_DIR):
        return []
    entries = []
    for name in os.listdir(FILES_DIR):
        if name.startswith("."):
            continue
        path = os.path.join(FILES_DIR, name)
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(name)[1].lower()
        entries.append({
            "name": name,
            "url": f"/static/files/{name}",
            "size": _human_size(os.path.getsize(path)),
            "label": EXTENSION_LABELS.get(ext, ext.lstrip(".").upper() or "ФАЙЛ"),
        })
    entries.sort(key=lambda e: e["name"].lower())
    return entries


@router.get("/", response_class=HTMLResponse)
async def list_files(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    """Страница с материалами для скачивания (прописи и т.п.)"""
    return templates.TemplateResponse(
        "public/files/list.html",
        {"request": request, "files": _list_files(), "user": current_user},
    )
