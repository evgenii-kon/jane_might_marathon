from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import Optional, List
from ..models.lesson import Lesson
from ..schemas.lesson import LessonCreate

class LessonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Lesson]:
        result = await self.db.execute(select(Lesson))
        return result.scalars().all()

    async def get_by_id(self, lesson_id: int) -> Optional[Lesson]:
        result = await self.db.execute(select(Lesson).where(Lesson.id == lesson_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, lesson_name: str) -> Optional[Lesson]:
        result = await self.db.execute(select(Lesson).where(Lesson.name == lesson_name))
        return result.scalar_one_or_none()

    async def create(self, lesson_data: LessonCreate) -> Lesson:
        new_lesson = Lesson(**lesson_data.model_dump())
        self.db.add(new_lesson)
        await self.db.commit()
        await self.db.refresh(new_lesson)
        return new_lesson

    async def update(self, lesson_id: int, update_data: dict) -> Optional[Lesson]:
        lesson = await self.get_by_id(lesson_id)
        if not lesson:
            return None
        for key, value in update_data.items():
            setattr(lesson, key, value)
        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def delete(self, lesson_id: int) -> bool:
        lesson = await self.get_by_id(lesson_id)
        if lesson:
            await self.db.delete(lesson)
            await self.db.commit()
            return True
        return False

    async def get_by_week_id(self, week_id: int) -> List[Lesson]:
        """Получить все уроки недели, отсортированные по порядку"""
        result = await self.db.execute(
            select(Lesson)
            .where(Lesson.week_id == week_id)
            .order_by(Lesson.order_in_week)
        )
        return result.scalars().all()

    async def get_count(self) -> int:
        """Получить общее количество уроков"""
        result = await self.db.execute(select(func.count(Lesson.id)))
        return result.scalar_one()