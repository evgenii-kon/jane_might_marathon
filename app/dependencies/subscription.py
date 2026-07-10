from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.lesson_repository import LessonRepository
from app.services.subscription_service import user_has_access
from app.services.week_service import WeekService


def require_feature(section: str):
    async def _check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_admin:
            return current_user
        has = await user_has_access(db, current_user.id, section)
        if not has:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/pricing"},
                detail="Subscription required",
            )
        return current_user
    return _check


def require_feature_or_trial_week(section: str):
    """Как require_feature, но неделя 1 всегда доступна без подписки."""
    async def _check(
        week_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_admin:
            return current_user

        week = await WeekService(db).get_week_by_id(week_id)
        if week.number == 1:
            return current_user

        has = await user_has_access(db, current_user.id, section)
        if not has:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/pricing"},
                detail="Subscription required",
            )
        return current_user
    return _check


def require_feature_or_trial_lesson(section: str):
    """Как require_feature, но уроки недели 1 всегда доступны без подписки."""
    async def _check(
        lesson_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_admin:
            return current_user

        lesson = await LessonRepository(db).get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
        if lesson.week.number == 1:
            return current_user

        has = await user_has_access(db, current_user.id, section)
        if not has:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/pricing"},
                detail="Subscription required",
            )
        return current_user
    return _check
