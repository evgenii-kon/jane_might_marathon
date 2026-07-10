from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.plan import Plan
from app.models.subscription import Subscription

SECTION_REQUIRED_FEATURE = {
    "lessons": "lessons",
    "exercises": "exercises",
    "word_trainer": "word_trainer",
    "weeks": "lessons",
    "idioms": "idioms",
    "grammar": "grammar",
    "reading": "reading",
}

ALL_FEATURES = ["lessons", "exercises", "word_trainer", "idioms", "grammar", "reading"]


async def get_active_plans(db: AsyncSession) -> List[Plan]:
    result = await db.execute(
        select(Plan).where(Plan.is_active == True).order_by(Plan.order)
    )
    return list(result.scalars().all())


async def get_plan_by_id(db: AsyncSession, plan_id: int) -> Optional[Plan]:
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    return result.scalar_one_or_none()


async def get_active_subscription(db: AsyncSession, user_id: int) -> Optional[Subscription]:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.expires_at > now,
        )
        .order_by(Subscription.expires_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_user_features(db: AsyncSession, user) -> List[str]:
    """Список фич, разблокированных для UI (замочки/бейджи). Админы видят всё разблокированным,
    так как require_feature() пропускает их независимо от подписки."""
    if user.is_admin:
        return list(ALL_FEATURES)
    sub = await get_active_subscription(db, user.id)
    if not sub or not sub.plan:
        return []
    return sub.plan.features or []


async def user_has_access(db: AsyncSession, user_id: int, section: str) -> bool:
    if section not in SECTION_REQUIRED_FEATURE:
        return True
    sub = await get_active_subscription(db, user_id)
    if not sub or not sub.plan:
        return False
    required = SECTION_REQUIRED_FEATURE[section]
    return required in (sub.plan.features or [])


async def create_pending_subscription(db: AsyncSession, user_id: int, plan_id: int) -> Subscription:
    sub = Subscription(user_id=user_id, plan_id=plan_id, status="pending")
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


async def activate_subscription(db: AsyncSession, sub: Subscription) -> Subscription:
    now = datetime.now(timezone.utc)
    sub.status = "active"
    sub.started_at = now
    sub.expires_at = now + timedelta(days=sub.plan.duration_days)
    await db.commit()
    await db.refresh(sub)
    return sub
