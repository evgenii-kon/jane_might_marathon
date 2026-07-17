from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import status, HTTPException
from ..repositories.novel_line_repository import NovelLineRepository
from ..schemas.novel_line import NovelLineCreate, NovelLineUpdate, NovelLineResponse
from ..services.cashe_service import CacheService


class NovelService:
    def __init__(self, db: AsyncSession):
        self.repository = NovelLineRepository(db)
        self.cache = CacheService(prefix="novel_lines", ttl=300)

    async def get_lines_by_lesson(self, lesson_id: int) -> List[NovelLineResponse]:
        """Получить реплики новеллы урока, отсортированные по порядку"""
        cached = await self.cache.get("lesson", lesson_id)
        if cached:
            return [NovelLineResponse.model_validate(l) for l in cached]

        lines = await self.repository.get_by_lesson_id(lesson_id)
        result = [NovelLineResponse.model_validate(line) for line in lines]
        await self.cache.set([l.model_dump(mode="json") for l in result], "lesson", lesson_id)
        return result

    async def get_lesson_ids_with_lines(self) -> List[int]:
        """Получить id уроков, у которых есть реплики новеллы"""
        return await self.repository.get_lesson_ids_with_lines()

    async def get_line_by_id(self, line_id: int) -> NovelLineResponse:
        """Получить реплику по id"""
        line = await self.repository.get_by_id(line_id)
        if not line:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Novel line with id={line_id} not found",
            )
        return NovelLineResponse.model_validate(line)

    async def create_line(self, data: NovelLineCreate) -> NovelLineResponse:
        """Создать реплику"""
        await self.cache.delete_pattern("*")
        line = await self.repository.create(data)
        return NovelLineResponse.model_validate(line)

    async def update_line(self, line_id: int, data: NovelLineUpdate) -> NovelLineResponse:
        """Обновить реплику"""
        existing = await self.repository.get_by_id(line_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Novel line with id={line_id} not found",
            )
        await self.cache.delete_pattern("*")
        update_dict = data.model_dump(exclude_unset=True)
        line = await self.repository.update(line_id, update_dict)
        return NovelLineResponse.model_validate(line)

    async def delete_line(self, line_id: int) -> bool:
        """Удалить реплику"""
        existing = await self.repository.get_by_id(line_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Novel line with id={line_id} not found",
            )
        await self.cache.delete_pattern("*")
        return await self.repository.delete(line_id)

    async def delete_lines_by_lesson(self, lesson_id: int) -> None:
        """Удалить все реплики урока"""
        await self.cache.delete_pattern("*")
        await self.repository.delete_by_lesson_id(lesson_id)
