from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
from typing import List
from app.models.user_word_progress import UserWordProgress


class UserWordProgressRepository:
    MASTERY_INTERVALS = {
        0: 1,  # не изучено
        1: 3,  # новичок
        2: 7,  # ученик
        3: 14,  # знаю
        4: 30,  # хорошо
        5: 60,  # мастер
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, user_id: int, word_id: int) -> UserWordProgress:
        result = await self.db.execute(
            select(UserWordProgress).where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.word_id == word_id
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = UserWordProgress(
                user_id=user_id,
                word_id=word_id,
                next_review_at=datetime.now(timezone.utc),
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)

        return progress

    async def update_mastery(
        self, user_id: int, word_id: int, is_correct: bool
    ) -> UserWordProgress:
        progress = await self.get_or_create(user_id, word_id)

        if is_correct:
            progress.correct_count += 1
            progress.mastery_level = min(5, progress.mastery_level + 1)
        else:
            progress.wrong_count += 1
            progress.mastery_level = max(0, progress.mastery_level - 1)

        interval_days = self.MASTERY_INTERVALS.get(progress.mastery_level, 1)
        progress.last_reviewed_at = datetime.now(timezone.utc)
        progress.next_review_at = datetime.now(timezone.utc) + timedelta(
            days=interval_days
        )

        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def get_words_for_review(
        self, user_id: int, limit: int = 30
    ) -> List[UserWordProgress]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(UserWordProgress)
            .options(selectinload(UserWordProgress.word))
            .where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.next_review_at <= now,
            )
            .order_by(UserWordProgress.next_review_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_by_user(self, user_id: int) -> List[UserWordProgress]:
        result = await self.db.execute(
            select(UserWordProgress).where(UserWordProgress.user_id == user_id)
        )
        return result.scalars().all()

    async def get_existing_word_ids(self, user_id: int) -> List[int]:
        """Получить ID слов, которые уже есть в прогрессе пользователя"""
        result = await self.db.execute(
            select(UserWordProgress.word_id).where(UserWordProgress.user_id == user_id)
        )
        return result.scalars().all()

    async def create_many(self, user_id: int, word_ids: List[int]) -> int:
        """Создать прогресс для нескольких слов"""
        if not word_ids:
            return 0

        now = datetime.now(timezone.utc)
        progresses = []
        for word_id in word_ids:
            progress = UserWordProgress(
                user_id=user_id,
                word_id=word_id,
                mastery_level=0,
                correct_count=0,
                wrong_count=0,
                next_review_at=now,
                last_reviewed_at=None,
            )
            progresses.append(progress)

        self.db.add_all(progresses)   # синхронный метод
        await self.db.commit()
        return len(progresses)

    async def get_review_count_today(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(func.count(UserWordProgress.id))
            .where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.next_review_at <= now,
            )
        )
        return result.scalar_one() or 0

    async def get_count(self, user_id: int) -> int:
        """Получить количество слов в прогрессе пользователя через COUNT"""
        result = await self.db.execute(
            select(func.count(UserWordProgress.id)).where(
                UserWordProgress.user_id == user_id
            )
        )
        return result.scalar_one() or 0

    async def get_mastery_stats(self, user_id: int) -> dict:
        result = await self.db.execute(
            select(UserWordProgress.mastery_level)
            .where(UserWordProgress.user_id == user_id)
        )
        levels = result.scalars().all()

        stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for level in levels:
            stats[level] = stats.get(level, 0) + 1

        return stats