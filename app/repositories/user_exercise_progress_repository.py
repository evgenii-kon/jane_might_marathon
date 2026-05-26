from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional, List, Dict
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
        """Получить прогресс по уроку (2 запроса COUNT вместо загрузки ID-списков)"""
        total_result = await self.db.execute(
            select(func.count(Exercise.id)).where(Exercise.lesson_id == lesson_id)
        )
        total = total_result.scalar_one()

        completed_result = await self.db.execute(
            select(func.count(UserExerciseProgress.id))
            .join(Exercise, UserExerciseProgress.exercise_id == Exercise.id)
            .where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.is_completed == True,
                Exercise.lesson_id == lesson_id,
            )
        )
        completed = completed_result.scalar_one()

        return {
            "total": total,
            "completed": completed,
            "percent": round(completed / total * 100, 1) if total > 0 else 0,
        }

    async def get_progress_by_lessons(
        self, user_id: int, lesson_ids: List[int]
    ) -> Dict[int, dict]:
        """Batch-получение прогресса упражнений для нескольких уроков (2 запроса вместо 2N)"""
        if not lesson_ids:
            return {}

        total_result = await self.db.execute(
            select(Exercise.lesson_id, func.count(Exercise.id))
            .where(Exercise.lesson_id.in_(lesson_ids))
            .group_by(Exercise.lesson_id)
        )
        total_by_lesson: Dict[int, int] = dict(total_result.fetchall())

        completed_result = await self.db.execute(
            select(Exercise.lesson_id, func.count(UserExerciseProgress.id))
            .join(Exercise, UserExerciseProgress.exercise_id == Exercise.id)
            .where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.is_completed == True,
                Exercise.lesson_id.in_(lesson_ids),
            )
            .group_by(Exercise.lesson_id)
        )
        completed_by_lesson: Dict[int, int] = dict(completed_result.fetchall())

        result: Dict[int, dict] = {}
        for lesson_id in lesson_ids:
            total = total_by_lesson.get(lesson_id, 0)
            completed = completed_by_lesson.get(lesson_id, 0)
            result[lesson_id] = {
                "total": total,
                "completed": completed,
                "percent": round(completed / total * 100, 1) if total > 0 else 0,
            }
        return result

    async def get_completed_count(self, user_id: int) -> int:
        """Получить общее количество пройденных упражнений"""
        result = await self.db.execute(
            select(func.count(UserExerciseProgress.id)).where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.is_completed == True,
            )
        )
        return result.scalar_one()

    async def reset_by_lesson(self, user_id: int, lesson_id: int) -> int:
        """Удалить весь прогресс упражнений пользователя для урока. Возвращает кол-во удалённых строк."""
        subq = (
            select(Exercise.id).where(Exercise.lesson_id == lesson_id).scalar_subquery()
        )
        result = await self.db.execute(
            delete(UserExerciseProgress).where(
                UserExerciseProgress.user_id == user_id,
                UserExerciseProgress.exercise_id.in_(subq),
            )
        )
        await self.db.commit()
        return result.rowcount