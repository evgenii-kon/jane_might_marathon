from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timezone
from app.models.user_lesson_progress import UserLessonProgress
from app.models.lesson import Lesson


class UserLessonProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_lesson(
        self, user_id: int, lesson_id: int
    ) -> Optional[UserLessonProgress]:
        """Получить прогресс пользователя по уроку"""
        result = await self.db.execute(
            select(UserLessonProgress).where(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.lesson_id == lesson_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Создать запись прогресса (урок начат, но не пройден)"""
        progress = UserLessonProgress(
            user_id=user_id, lesson_id=lesson_id, is_completed=False, completed_at=None
        )
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def mark_completed(self, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Отметить урок как пройденный"""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)

        if not progress:
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=datetime.now(timezone.utc),
            )
            self.db.add(progress)
        else:
            progress.is_completed = True
            progress.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def mark_started(self, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Отметить урок как начатый"""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)

        if not progress:
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_started=True,
                is_completed=False,
            )
            self.db.add(progress)
        else:
            progress.is_started = True

        await self.db.commit()
        await self.db.refresh(progress)
        return progress

    async def is_completed(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, пройден ли урок"""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)
        return progress is not None and progress.is_completed

    async def is_started(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, начат ли урок"""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)
        return progress is not None and progress.is_started

    async def get_completed_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID пройденных уроков пользователя"""
        result = await self.db.execute(
            select(UserLessonProgress.lesson_id)
            .where(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.is_completed == True,
            )
        )
        return result.scalars().all()

    async def get_started_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID начатых уроков пользователя"""
        result = await self.db.execute(
            select(UserLessonProgress.lesson_id)
            .where(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.is_started == True,
            )
        )
        return result.scalars().all()

    async def get_completed_count_by_user(self, user_id: int) -> int:
        """Получить количество пройденных уроков пользователя"""
        result = await self.db.execute(
            select(func.count(UserLessonProgress.id))
            .where(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.is_completed == True,
            )
        )
        return result.scalar_one() or 0

    async def mark_exercises_ever_completed(self, user_id: int, lesson_id: int) -> None:
        """Навсегда выставить флаг 'упражнения были пройдены хотя бы раз'. Не сбрасывается."""
        progress = await self.get_by_user_and_lesson(user_id, lesson_id)
        if progress is None:
            # На случай рассинхронизации — создаём запись
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_started=True,
                is_completed=True,
                exercises_ever_completed=True,
            )
            self.db.add(progress)
        elif not progress.exercises_ever_completed:
            progress.exercises_ever_completed = True
        else:
            return  # Уже выставлен, ничего не делаем
        await self.db.commit()

    async def get_exercises_ever_completed_lesson_ids(self, user_id: int) -> List[int]:
        """Вернуть lesson_id уроков, где упражнения были полностью пройдены хотя бы раз."""
        result = await self.db.execute(
            select(UserLessonProgress.lesson_id).where(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.exercises_ever_completed == True,
            )
        )
        return result.scalars().all()

    async def get_completed_count_by_week(self, user_id: int, week_id: int) -> int:
        """Получить количество пройденных уроков в конкретной неделе"""
        result = await self.db.execute(
            select(func.count(UserLessonProgress.id))
            .join(Lesson, Lesson.id == UserLessonProgress.lesson_id)
            .where(
                UserLessonProgress.user_id == user_id,
                Lesson.week_id == week_id,
                UserLessonProgress.is_completed == True,
            )
        )
        return result.scalar_one() or 0