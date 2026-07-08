from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.user_idiom_progress import UserIdiomProgress


class UserIdiomProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int, idiom_id: int) -> Optional[UserIdiomProgress]:
        """Получить прогресс пользователя по идиоме"""
        result = await self.db.execute(
            select(UserIdiomProgress).where(
                UserIdiomProgress.user_id == user_id,
                UserIdiomProgress.idiom_id == idiom_id,
            )
        )
        return result.scalar_one_or_none()

    async def set_status(self, user_id: int, idiom_id: int, status: str) -> UserIdiomProgress:
        """Установить статус прогресса идиомы для пользвателя"""
        progress = await self.get(user_id, idiom_id)
        if progress:
            progress.status = status
        else:
            progress = UserIdiomProgress(user_id=user_id, idiom_id=idiom_id, status=status)
            self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def get_all_by_user(self, user_id: int) -> List[UserIdiomProgress]:
        """Получить прогресс по всем идиомам для пользователя"""
        result = await self.db.execute(
            select(UserIdiomProgress).where(UserIdiomProgress.user_id == user_id)
        )
        return result.scalars().all()
