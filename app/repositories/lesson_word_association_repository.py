from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.lesson_word_association import lesson_word_association

class LessonWordAssociationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_word_ids_by_lesson(self, lesson_id: int) -> List[int]:
        """Получить все ID слов, связанных с уроком"""
        result = await self.db.execute(
            select(lesson_word_association.c.word_id)
            .where(lesson_word_association.c.lesson_id == lesson_id)
        )
        return list(result.scalars().all())