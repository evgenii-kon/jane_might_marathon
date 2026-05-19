from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/admin/feedback", tags=["admin_feedback"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_feedback(
    request: Request,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = FeedbackService(db)
    return templates.TemplateResponse("admin/feedback/feedback_list.html", {
        "request": request,
        "feedbacks": service.get_all(),
        "user": admin
    })


@router.get("/{feedback_id}", response_class=HTMLResponse)
def view_feedback(
    request: Request,
    feedback_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = FeedbackService(db)
    feedback = service.get_by_id(feedback_id)
    if not feedback:
        return RedirectResponse(url="/admin/feedback", status_code=302)
    return templates.TemplateResponse("admin/feedback/feedback_detail.html", {
        "request": request,
        "feedback": feedback,
        "user": admin
    })


@router.post("/{feedback_id}/delete")
def delete_feedback(
    feedback_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = FeedbackService(db)
    service.delete(feedback_id)
    return RedirectResponse(url="/admin/feedback", status_code=302)


@router.get("/{feedback_id}/delete", response_class=HTMLResponse)
def delete_feedback_confirm(
    request: Request,
    feedback_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = FeedbackService(db)
    feedback = service.get_by_id(feedback_id)
    return templates.TemplateResponse("admin/feedback/delete_confirm.html", {
        "request": request,
        "feedback": feedback,
        "user": admin
    })