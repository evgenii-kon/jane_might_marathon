from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Set

from ..models.user_reading_progress import UserReadingProgress


class UserReadingProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int, text_id: int) -> Optional[UserReadingProgress]:
        """Получить прогресс пользователя по тексту"""
        result = await self.db.execute(
            select(UserReadingProgress).where(
                UserReadingProgress.user_id == user_id,
                UserReadingProgress.text_id == text_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_completed_ids(self, user_id: int) -> Set[int]:
        """Получить id текстов, которые пользователь прошел"""
        result = await self.db.execute(
            select(UserReadingProgress.text_id).where(
                UserReadingProgress.user_id == user_id,
                UserReadingProgress.is_completed == True,
            )
        )
        return set(result.scalars().all())

    async def mark_completed(self, user_id: int, text_id: int) -> UserReadingProgress:
        """Отметить текст пройденным"""
        existing = await self.get(user_id, text_id)
        if existing:
            existing.is_completed = True
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        obj = UserReadingProgress(user_id=user_id, text_id=text_id, is_completed=True)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
