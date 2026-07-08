from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models.reading_text import ReadingText
from ..schemas.reading import ReadingTextCreate


class ReadingTextRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[ReadingText]:
        """Получить все тексты, отсортированные от новых к старым"""
        result = await self.db.execute(
            select(ReadingText)
            .options(selectinload(ReadingText.questions))
            .order_by(ReadingText.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, text_id: int) -> Optional[ReadingText]:
        """Получить текст по id"""
        result = await self.db.execute(
            select(ReadingText)
            .options(selectinload(ReadingText.questions))
            .where(ReadingText.id == text_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[ReadingText]:
        """Получить текст по slug"""
        result = await self.db.execute(
            select(ReadingText)
            .options(selectinload(ReadingText.questions))
            .where(ReadingText.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ReadingTextCreate) -> ReadingText:
        """Сощздать текст"""
        obj = ReadingText(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, text_id: int, update_data: dict) -> Optional[ReadingText]:
        """Обновить текст"""
        obj = await self.get_by_id(text_id)
        if not obj:
            return None
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, text_id: int) -> bool:
        """Удалить текст"""
        obj = await self.get_by_id(text_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

    async def count(self) -> int:
        """Общее количество текстов"""
        result = await self.db.execute(select(func.count()).select_from(ReadingText))
        return result.scalar_one()
