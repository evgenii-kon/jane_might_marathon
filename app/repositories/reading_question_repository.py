from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ..models.reading_question import ReadingQuestion
from ..schemas.reading import ReadingQuestionCreate


class ReadingQuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_text_id(self, text_id: int) -> List[ReadingQuestion]:
        result = await self.db.execute(
            select(ReadingQuestion)
            .where(ReadingQuestion.text_id == text_id)
            .order_by(ReadingQuestion.order_in_text)
        )
        return result.scalars().all()

    async def get_by_id(self, question_id: int) -> Optional[ReadingQuestion]:
        result = await self.db.execute(
            select(ReadingQuestion).where(ReadingQuestion.id == question_id)
        )
        return result.scalar_one_or_none()

    async def create(self, text_id: int, data: ReadingQuestionCreate) -> ReadingQuestion:
        obj = ReadingQuestion(text_id=text_id, **data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, question_id: int, update_data: dict) -> Optional[ReadingQuestion]:
        obj = await self.get_by_id(question_id)
        if not obj:
            return None
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, question_id: int) -> bool:
        obj = await self.get_by_id(question_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
