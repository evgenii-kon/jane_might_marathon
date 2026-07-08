from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from ..models.exercise import Exercise
from ..schemas.exercise import ExerciseCreate

class ExerciseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Exercise]:
        """Получить все упражнения"""
        result = await self.db.execute(select(Exercise))
        return result.scalars().all()

    async def get_by_lesson(self, lesson_id: int) -> List[Exercise]:
        """Получить упражнение по уроку"""
        result = await self.db.execute(
            select(Exercise)
            .where(Exercise.lesson_id == lesson_id)
            .order_by(Exercise.order_in_lesson)
        )
        return result.scalars().all()

    async def get_by_id(self, exercise_id: int) -> Optional[Exercise]:
        """Получить упражнение по id"""
        result = await self.db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        return result.scalar_one_or_none()

    async def get_count_by_lesson(self, lesson_id: int) -> int:
        """Получить количество упражнений в уроке"""
        result = await self.db.execute(
            select(func.count(Exercise.id)).where(Exercise.lesson_id == lesson_id)
        )
        return result.scalar_one()

    async def create(self, data: ExerciseCreate) -> Exercise:
        """Создать упражнение"""
        exercise = Exercise(**data.model_dump())
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def update(self, exercise_id: int, data: dict) -> Optional[Exercise]:
        """Обновить упражнение"""
        exercise = await self.get_by_id(exercise_id)
        if exercise:
            for key, value in data.items():
                setattr(exercise, key, value)
            await self.db.commit()
            await self.db.refresh(exercise)
        return exercise

    async def delete(self, exercise_id: int) -> bool:
        """Удалить упражнение"""
        exercise = await self.get_by_id(exercise_id)
        if exercise:
            await self.db.delete(exercise)
            await self.db.commit()
            return True
        return False