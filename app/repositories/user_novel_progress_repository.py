from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ..models.user_novel_progress import UserNovelProgress


class UserNovelProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_lesson(self, user_id: int, lesson_id: int) -> Optional[UserNovelProgress]:
        """Получить запись о просмотре новеллы пользователем"""
        result = await self.db.execute(
            select(UserNovelProgress).where(
                UserNovelProgress.user_id == user_id,
                UserNovelProgress.lesson_id == lesson_id,
            )
        )
        return result.scalar_one_or_none()

    async def has_seen(self, user_id: int, lesson_id: int) -> bool:
        """Видел ли пользователь новеллу перед этим уроком хотя бы раз"""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)
        return progress is not None

    async def mark_seen(self, user_id: int, lesson_id: int) -> UserNovelProgress:
        """Отметить новеллу урока как просмотренную (идемпотентно)"""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)
        if progress:
            return progress
        progress = UserNovelProgress(user_id=user_id, lesson_id=lesson_id)
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)
        return progress
