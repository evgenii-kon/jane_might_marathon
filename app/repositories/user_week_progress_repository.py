from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timezone
from app.models.user_week_progress import UserWeekProgress


class UserWeekProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_week(
        self, user_id: int, week_id: int
    ) -> Optional[UserWeekProgress]:
        """Получить прогресс пользователя по конкретной неделе"""
        result = await self.db.execute(
            select(UserWeekProgress).where(
                UserWeekProgress.user_id == user_id,
                UserWeekProgress.week_id == week_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> List[UserWeekProgress]:
        """Получить весь прогресс пользователя по неделям"""
        result = await self.db.execute(
            select(UserWeekProgress).where(UserWeekProgress.user_id == user_id)
        )
        return result.scalars().all()

    async def create(
        self, user_id: int, week_id: int, opens_at: datetime
    ) -> UserWeekProgress:
        """Создать запись прогресса для недели"""
        progress = UserWeekProgress(user_id=user_id, week_id=week_id, opens_at=opens_at)
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def create_many(self, user_id: int, weeks_opens_at: List[tuple]) -> int:
        """Создать записи прогресса для нескольких недель сразу"""
        progresses = []
        for week_id, opens_at in weeks_opens_at:
            progress = UserWeekProgress(
                user_id=user_id, week_id=week_id, opens_at=opens_at
            )
            progresses.append(progress)

        self.db.add_all(progresses)           # синхронный метод, без await
        await self.db.commit()
        return len(progresses)

    async def update(self, progress_id: int, update_data: dict) -> Optional[UserWeekProgress]:
        """Обновить прогресс"""
        result = await self.db.execute(
            select(UserWeekProgress).where(UserWeekProgress.id == progress_id)
        )
        progress = result.scalar_one_or_none()

        if not progress:
            return None

        for key, value in update_data.items():
            setattr(progress, key, value)

        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def mark_completed(self, user_id: int, week_id: int) -> Optional[UserWeekProgress]:
        """Отметить неделю как пройденную"""
        progress = await self.get_by_user_and_week(user_id, week_id)
        if progress and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(progress)
        return progress

    async def get_completed_week_ids(self, user_id: int) -> List[int]:
        """Получить ID всех пройденных недель"""
        result = await self.db.execute(
            select(UserWeekProgress.week_id)
            .where(
                UserWeekProgress.user_id == user_id,
                UserWeekProgress.is_completed == True,
            )
        )
        return result.scalars().all()