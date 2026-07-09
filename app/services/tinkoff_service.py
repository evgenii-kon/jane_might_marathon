import hashlib
import uuid
import httpx
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.payment import Payment
from app.models.subscription import Subscription

TINKOFF_API_URL = "https://securepay.tinkoff.ru/v2"


def _generate_token(params: dict) -> str:
    excluded = {"Token", "Receipt", "DATA", "Items"}
    filtered = {k: str(v) for k, v in params.items() if k not in excluded}
    filtered["Password"] = settings.TINKOFF_PASSWORD
    sorted_values = "".join(v for _, v in sorted(filtered.items()))
    return hashlib.sha256(sorted_values.encode()).hexdigest()


def _verify_notification_token(params: dict) -> bool:
    received_token = params.get("Token", "")
    expected = _generate_token(params)
    return received_token == expected


async def create_payment(
    db: AsyncSession,
    subscription: Subscription,
    user_id: int,
    amount_kopecks: int,
    description: str,
    email: str,
) -> Payment:
    order_id = f"sub-{subscription.id}-{uuid.uuid4().hex[:8]}"
    init_params = {
        "TerminalKey": settings.TINKOFF_TERMINAL_KEY,
        "Amount": amount_kopecks,
        "OrderId": order_id,
        "Description": description,
        "NotificationURL": f"{settings.APP_URL}/payment/webhook",
        "SuccessURL": f"{settings.APP_URL}/payment/success",
        "FailURL": f"{settings.APP_URL}/payment/fail",
    }
    init_params["Token"] = _generate_token(init_params)
    init_params["Receipt"] = {
        "Email": email,
        "Taxation": "usn_income",
        "Items": [{
            "Name": description[:128],
            "Price": amount_kopecks,
            "Quantity": 1.00,
            "Amount": amount_kopecks,
            "Tax": "none",
            "PaymentMethod": "full_payment",
            "PaymentObject": "service",
        }],
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{TINKOFF_API_URL}/Init", json=init_params)
        data = resp.json()
    if not data.get("Success"):
        raise RuntimeError(f"Tinkoff Init error: {data.get('Message')}")
    payment = Payment(
        subscription_id=subscription.id,
        user_id=user_id,
        tinkoff_payment_id=str(data["PaymentId"]),
        order_id=order_id,
        amount_kopecks=amount_kopecks,
        status=data.get("Status", "NEW"),
        payment_url=data.get("PaymentURL"),
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def handle_notification(db: AsyncSession, payload: dict) -> bool:
    if not _verify_notification_token(payload):
        return False
    payment_id = str(payload.get("PaymentId"))
    status = payload.get("Status", "")
    result = await db.execute(select(Payment).where(Payment.tinkoff_payment_id == payment_id))
    payment: Optional[Payment] = result.scalar_one_or_none()
    if not payment:
        return False
    payment.status = status
    if status == "CONFIRMED":
        payment.confirmed_at = datetime.now(timezone.utc)
        result = await db.execute(select(Subscription).where(Subscription.id == payment.subscription_id))
        sub: Optional[Subscription] = result.scalar_one_or_none()
        if sub and sub.status != "active":
            from app.services.subscription_service import activate_subscription
            await activate_subscription(db, sub)
    await db.commit()
    return True
