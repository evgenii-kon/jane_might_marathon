from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.subscription_service import (
    get_active_plans, get_plan_by_id, get_active_subscription, create_pending_subscription,
)
from app.services.tinkoff_service import create_payment, handle_notification
from app.csrf import get_csrf_token

router = APIRouter(tags=["payment"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    plans = await get_active_plans(db)
    active_sub = None
    if current_user:
        active_sub = await get_active_subscription(db, current_user.id)
    return templates.TemplateResponse("payment/pricing.html", {
        "request": request,
        "user": current_user,
        "plans": plans,
        "active_sub": active_sub,
        "csrf_token": get_csrf_token(request),
    })


@router.post("/payment/create")
async def payment_create(
    request: Request,
    plan_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await get_plan_by_id(db, plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Тариф не найден")
    existing = await get_active_subscription(db, current_user.id)
    if existing:
        return RedirectResponse("/dashboard", status_code=302)
    subscription = await create_pending_subscription(db, current_user.id, plan.id)
    payment = await create_payment(
        db=db,
        subscription=subscription,
        user_id=current_user.id,
        amount_kopecks=plan.price_kopecks,
        description=f"Курс HSK-1 — тариф «{plan.name}»",
        email=current_user.email,
    )
    return RedirectResponse(payment.payment_url, status_code=302)


@router.post("/payment/webhook")
async def payment_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    ok = await handle_notification(db, payload)
    return JSONResponse(content="OK" if ok else "ERROR")


@router.get("/payment/success", response_class=HTMLResponse)
async def payment_success(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    sub = None
    if current_user:
        sub = await get_active_subscription(db, current_user.id)
    return templates.TemplateResponse("payment/success.html", {
        "request": request, "user": current_user, "subscription": sub,
    })


@router.get("/payment/fail", response_class=HTMLResponse)
async def payment_fail(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    return templates.TemplateResponse("payment/fail.html", {
        "request": request, "user": current_user,
    })
