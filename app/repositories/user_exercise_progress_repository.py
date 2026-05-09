from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func
from ..models.user_exercise_progress import UserExerciseProgress
from ..models.exercise import Exercise


class UserExerciseProgressRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_by_user_and_exercise(self, user_id: int, exercise_id: int) -> Optional[UserExerciseProgress]:
        """Получить прогресс по конкретному упражнению"""
        return self.db.query(UserExerciseProgress).filter(
            UserExerciseProgress.user_id == user_id,
            UserExerciseProgress.exercise_id == exercise_id
        ).first()


    def mark_completed(self, user_id: int, exercise_id: int) -> UserExerciseProgress:
        """Отметить упражнение как пройденное"""
        progress = self.get_by_user_and_exercise(user_id, exercise_id)
        from datetime import datetime
        
        if not progress:
            progress = UserExerciseProgress(
                user_id=user_id,
                exercise_id=exercise_id,
                is_completed=True,
                completed_at=datetime.now()
            )
            self.db.add(progress)
        else:
            progress.is_completed = True
            progress.completed_at = datetime.now()
        
        self.db.commit()
        return progress


    def get_completed_ids_by_lesson(self, user_id: int, lesson_id: int) -> List[int]:
        """Получить ID упражнений, пройденных пользователем в уроке"""
        results = self.db.query(UserExerciseProgress.exercise_id).join(
            Exercise, UserExerciseProgress.exercise_id == Exercise.id
        ).filter(
            UserExerciseProgress.user_id == user_id,
            UserExerciseProgress.is_completed == True,
            Exercise.lesson_id == lesson_id
        ).all()
        return [r[0] for r in results]


    def get_progress_by_lesson(self, user_id: int, lesson_id: int) -> dict:
        """Получить прогресс по уроку"""
        total = self.db.query(Exercise).filter(Exercise.lesson_id == lesson_id).count()
        completed = len(self.get_completed_ids_by_lesson(user_id, lesson_id))
        
        return {
            'total': total,
            'completed': completed,
            'percent': round(completed / total * 100, 1) if total > 0 else 0
        }


    def get_completed_count(self, user_id: int) -> int:
        """Получить общее количество пройденных упражнений"""
        return self.db.query(UserExerciseProgress).filter(
            UserExerciseProgress.user_id == user_id,
            UserExerciseProgress.is_completed == True
        ).count()