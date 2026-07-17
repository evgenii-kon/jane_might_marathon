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
