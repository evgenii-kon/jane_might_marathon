from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/complete-novel-onboarding")
async def complete_novel_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Отмечает, что пользователь досмотрел комикс-онбординг"""
    user_service = UserService(db)
    await user_service.update_user_by_id(current_user.id, {"novel_onboarding_completed": True})
    return {"ok": True}


@router.post("/reset-novel-onboarding")
async def reset_novel_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сбрасывает флаг — комикс покажется снова при следующем открытии страницы"""
    user_service = UserService(db)
    await user_service.update_user_by_id(current_user.id, {"novel_onboarding_completed": False})
    return {"ok": True}


@router.post("/skip-novel")
async def skip_novel(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Пользователь решил пропускать сюжетные сцены перед уроками"""
    user_service = UserService(db)
    await user_service.update_user_by_id(
        current_user.id,
        {
            "novel_skipped": True,
            "novel_skipped_at": datetime.now(timezone.utc),
            "novel_skip_asked": True,
        },
    )
    return {"ok": True}


@router.post("/unskip-novel")
async def unskip_novel(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Пользователь решил оставить сюжетные сцены перед уроками"""
    user_service = UserService(db)
    await user_service.update_user_by_id(
        current_user.id,
        {"novel_skipped": False, "novel_skip_asked": True},
    )
    return {"ok": True}
