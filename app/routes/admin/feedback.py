from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/admin/feedback", tags=["admin_feedback"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_feedback(
    request: Request,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = FeedbackService(db)
    feedbacks = await service.get_all()
    return templates.TemplateResponse("admin/feedback/feedback_list.html", {
        "request": request,
        "feedbacks": feedbacks,
        "user": admin,
        "csrf_token": getattr(request.state, "csrf_token", request.cookies.get("csrftoken", "")),
    })


@router.get("/{feedback_id}", response_class=HTMLResponse)
async def view_feedback(
    request: Request,
    feedback_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = FeedbackService(db)
    try:
        feedback = await service.get_by_id(feedback_id)
    except HTTPException as e:
        if e.status_code == 404:
            return RedirectResponse(url="/admin/feedback", status_code=302)
        raise
    if not feedback:
        return RedirectResponse(url="/admin/feedback", status_code=302)
    return templates.TemplateResponse("admin/feedback/feedback_detail.html", {
        "request": request,
        "feedback": feedback,
        "user": admin
    })


@router.post("/{feedback_id}/delete")
async def delete_feedback(
    feedback_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = FeedbackService(db)
    await service.delete(feedback_id)
    return RedirectResponse(url="/admin/feedback", status_code=302)


@router.get("/{feedback_id}/delete", response_class=HTMLResponse)
async def delete_feedback_confirm(
    request: Request,
    feedback_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    service = FeedbackService(db)
    try:
        feedback = await service.get_by_id(feedback_id)
    except HTTPException as e:
        if e.status_code == 404:
            return RedirectResponse(url="/admin/feedback", status_code=302)
        raise
    return templates.TemplateResponse("admin/feedback/delete_confirm.html", {
        "request": request,
        "feedback": feedback,
        "user": admin,
        "csrf_token": getattr(request.state, "csrf_token", request.cookies.get("csrftoken", "")),
    })