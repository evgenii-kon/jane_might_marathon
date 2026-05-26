from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from fastapi import HTTPException
from ..repositories.user_exercise_progress_repository import (
    UserExerciseProgressRepository,
)
from ..repositories.exercise_repository import ExerciseRepository
from ..repositories.user_lesson_progress_repository import UserLessonProgressRepository
from ..schemas.user_exercise_progress import (
    UserExerciseProgressResponse,
    LessonExerciseProgressResponse,
)


class UserExerciseProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserExerciseProgressRepository(db)
        self.exercise_repo = ExerciseRepository(db)
        self.lesson_progress_repo = UserLessonProgressRepository(db)

    async def is_lesson_completed(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, пройден ли урок"""
        return await self.lesson_progress_repo.is_completed(user_id, lesson_id)

    async def is_exercise_completed(self, user_id: int, exercise_id: int) -> bool:
        """Проверить, пройдено ли упражнение"""
        progress = await self.repository.get_by_user_and_exercise(user_id, exercise_id)
        return progress is not None and progress.is_completed

    async def mark_exercise_completed(
        self, user_id: int, exercise_id: int
    ) -> UserExerciseProgressResponse:
        """Отметить упражнение как пройденное"""
        exercise = await self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=404, detail=f"Exercise {exercise_id} not found"
            )

        progress = await self.repository.mark_completed(user_id, exercise_id)
        return UserExerciseProgressResponse.model_validate(progress)

    async def get_completed_exercise_ids(self, user_id: int, lesson_id: int) -> List[int]:
        """Получить ID пройденных упражнений в уроке"""
        return await self.repository.get_completed_ids_by_lesson(user_id, lesson_id)

    async def get_lesson_progress(
        self, user_id: int, lesson_id: int
    ) -> LessonExerciseProgressResponse:
        """Получить прогресс по уроку"""
        progress = await self.repository.get_progress_by_lesson(user_id, lesson_id)
        return LessonExerciseProgressResponse(
            total=progress["total"],
            completed=progress["completed"],
            percent=progress["percent"],
        )

    async def get_total_completed_count(self, user_id: int) -> int:
        """Получить общее количество пройденных упражнений"""
        return await self.repository.get_completed_count(user_id)

    async def get_lessons_progress(
        self, user_id: int, lesson_ids: List[int]
    ) -> Dict[int, LessonExerciseProgressResponse]:
        """Batch-получение прогресса упражнений для нескольких уроков за 2 запроса"""
        raw = await self.repository.get_progress_by_lessons(user_id, lesson_ids)
        return {
            lesson_id: LessonExerciseProgressResponse(
                total=data["total"],
                completed=data["completed"],
                percent=data["percent"],
            )
            for lesson_id, data in raw.items()
        }