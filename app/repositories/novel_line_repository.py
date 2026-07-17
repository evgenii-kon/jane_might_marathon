from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List
from ..models.novel_line import NovelLine
from ..schemas.novel_line import NovelLineCreate


class NovelLineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_lesson_id(self, lesson_id: int) -> List[NovelLine]:
        """Получить все реплики урока, отсортированные по порядку"""
        result = await self.db.execute(
            select(NovelLine)
            .where(NovelLine.lesson_id == lesson_id)
            .order_by(NovelLine.order)
        )
        return result.scalars().all()

    async def get_by_id(self, line_id: int) -> Optional[NovelLine]:
        """Получить реплику по id"""
        result = await self.db.execute(select(NovelLine).where(NovelLine.id == line_id))
        return result.scalar_one_or_none()

    async def get_lesson_ids_with_lines(self) -> List[int]:
        """Получить id уроков, у которых есть хотя бы одна реплика новеллы"""
        result = await self.db.execute(select(NovelLine.lesson_id).distinct())
        return result.scalars().all()

    async def create(self, data: NovelLineCreate) -> NovelLine:
        """Создать реплику"""
        line = NovelLine(**data.model_dump())
        self.db.add(line)
        await self.db.commit()
        await self.db.refresh(line)
        return line

    async def update(self, line_id: int, data: dict) -> Optional[NovelLine]:
        """Обновить реплику"""
        line = await self.get_by_id(line_id)
        if not line:
            return None
        for key, value in data.items():
            setattr(line, key, value)
        await self.db.commit()
        await self.db.refresh(line)
        return line

    async def delete(self, line_id: int) -> bool:
        """Удалить реплику"""
        line = await self.get_by_id(line_id)
        if line:
            await self.db.delete(line)
            await self.db.commit()
            return True
        return False

    async def delete_by_lesson_id(self, lesson_id: int) -> None:
        """Удалить все реплики урока"""
        await self.db.execute(delete(NovelLine).where(NovelLine.lesson_id == lesson_id))
        await self.db.commit()
