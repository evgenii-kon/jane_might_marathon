from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.exercise import Exercise
from ..schemas.exercise import ExerciseCreate


class ExerciseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Exercise]:
        return self.db.query(Exercise).all()

    def get_by_lesson(self, lesson_id: int) -> List[Exercise]:
        return (
            self.db.query(Exercise)
            .filter(Exercise.lesson_id == lesson_id)
            .order_by(Exercise.order_in_lesson)
            .all()
        )

    def get_by_id(self, exercise_id: int) -> Optional[Exercise]:
        return self.db.query(Exercise).filter(Exercise.id == exercise_id).first()

    def get_count_by_lesson(self, lesson_id: int) -> int:
        """Получить количество упражнений в уроке"""
        return self.db.query(Exercise).filter(Exercise.lesson_id == lesson_id).count()

    def create(self, data: ExerciseCreate) -> Exercise:
        exercise = Exercise(**data.model_dump())
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def update(self, exercise_id: int, data: dict) -> Optional[Exercise]:
        exercise = self.get_by_id(exercise_id)
        if exercise:
            for key, value in data.items():
                setattr(exercise, key, value)
            self.db.commit()
            self.db.refresh(exercise)
        return exercise

    def delete(self, exercise_id: int) -> bool:
        exercise = self.get_by_id(exercise_id)
        if exercise:
            self.db.delete(exercise)
            self.db.commit()
            return True
        return False
