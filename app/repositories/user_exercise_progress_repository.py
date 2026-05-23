from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from ..models.user_exercise_progress import UserExerciseProgress
from ..models.exercise import Exercise
from datetime import datetime, timezone


class UserExerciseProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_exercise(
        self, user_id: int, exercise_id: int
    ) -> Optional[UserExerciseProgress]:
        """Получить прогресс по конкретному упражнению"""
        result = await self.db.execute(
            select(UserExerciseProgress).where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.exercise_id == exercise_id
            )
        )
        return result.scalar_one_or_none()

    async def mark_completed(self, user_id: int, exercise_id: int) -> UserExerciseProgress:
        """Отметить упражнение как пройденное"""
        progress = await self.get_by_user_and_exercise(user_id, exercise_id)

        if not progress:
            progress = UserExerciseProgress(
                user_id=user_id,
                exercise_id=exercise_id,
                is_completed=True,
                completed_at=datetime.now(timezone.utc),
            )
            self.db.add(progress)
        else:
            progress.is_completed = True
            progress.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        # Обновляем объект, чтобы он был привязан к сессии (если нужно)
        await self.db.refresh(progress)
        return progress

    async def get_completed_ids_by_lesson(self, user_id: int, lesson_id: int) -> List[int]:
        """Получить ID упражнений, пройденных пользователем в уроке"""
        result = await self.db.execute(
            select(UserExerciseProgress.exercise_id)
            .join(Exercise, UserExerciseProgress.exercise_id == Exercise.id)
            .where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.is_completed == True,
                Exercise.lesson_id == lesson_id,
            )
        )
        return result.scalars().all()

    async def get_progress_by_lesson(self, user_id: int, lesson_id: int) -> dict:
        """Получить прогресс по уроку"""
        # общее количество упражнений в уроке
        total_result = await self.db.execute(
            select(func.count(Exercise.id)).where(Exercise.lesson_id == lesson_id)
        )
        total = total_result.scalar_one()

        # количество пройденных упражнений
        completed = len(await self.get_completed_ids_by_lesson(user_id, lesson_id))

        return {
            "total": total,
            "completed": completed,
            "percent": round(completed / total * 100, 1) if total > 0 else 0,
        }

    async def get_completed_count(self, user_id: int) -> int:
        """Получить общее количество пройденных упражнений"""
        result = await self.db.execute(
            select(func.count(UserExerciseProgress.id)).where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.is_completed == True,
            )
        )
        return result.scalar_one()