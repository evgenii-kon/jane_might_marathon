from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from ..repositories.user_exercise_progress_repository import UserExerciseProgressRepository
from ..repositories.exercise_repository import ExerciseRepository
from ..repositories.user_lesson_progress_repository import UserLessonProgressRepository
from ..schemas.user_exercise_progress import UserExerciseProgressResponse, LessonExerciseProgressResponse


class UserExerciseProgressService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserExerciseProgressRepository(db)
        self.exercise_repo = ExerciseRepository(db)
        self.lesson_progress_repo = UserLessonProgressRepository(db)


    def is_lesson_completed(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, пройден ли урок"""
        return self.lesson_progress_repo.is_completed(user_id, lesson_id)


    def is_exercise_completed(self, user_id: int, exercise_id: int) -> bool:
        """Проверить, пройдено ли упражнение"""
        progress = self.repository.get_by_user_and_exercise(user_id, exercise_id)
        return progress is not None and progress.is_completed


    def mark_exercise_completed(self, user_id: int, exercise_id: int) -> UserExerciseProgressResponse:
        """Отметить упражнение как пройденное"""
        exercise = self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail=f"Exercise {exercise_id} not found")
        
        progress = self.repository.mark_completed(user_id, exercise_id)
        return UserExerciseProgressResponse.model_validate(progress)


    def get_completed_exercise_ids(self, user_id: int, lesson_id: int) -> List[int]:
        """Получить ID пройденных упражнений в уроке"""
        return self.repository.get_completed_ids_by_lesson(user_id, lesson_id)


    def get_lesson_progress(self, user_id: int, lesson_id: int) -> LessonExerciseProgressResponse:
        """Получить прогресс по уроку"""
        progress = self.repository.get_progress_by_lesson(user_id, lesson_id)
        return LessonExerciseProgressResponse(
            total=progress['total'],
            completed=progress['completed'],
            percent=progress['percent']
        )


    def get_total_completed_count(self, user_id: int) -> int:
        """Получить общее количество пройденных упражнений"""
        return self.repository.get_completed_count(user_id)