from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..repositories.lesson_repository import LessonRepository
from ..schemas.lesson import LessonCreate, LessonResponse, LessonUpdate
from fastapi import status, HTTPException


class LessonService:
    def __init__(self, db: AsyncSession):
        self.repository = LessonRepository(db)

    async def get_all_lessons(self) -> List[LessonResponse]:
        lessons = await self.repository.get_all()
        return [LessonResponse.model_validate(lesson) for lesson in lessons]

    async def get_lesson_by_id(self, lesson_id: int) -> LessonResponse:
        lesson = await self.repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"lesson with id={lesson_id} not found",
            )
        return LessonResponse.model_validate(lesson)

    async def create_lesson(self, lesson_data: LessonCreate) -> LessonResponse:
        lesson_exist_check = await self.repository.get_by_name(lesson_data.name)
        if lesson_exist_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lesson with name {lesson_data.name} is already exist",
            )
        new_lesson = await self.repository.create(lesson_data)
        return LessonResponse.model_validate(new_lesson)

    async def update_lesson(
        self, lesson_id: int, lesson_data: LessonUpdate
    ) -> LessonResponse:
        lesson_exist_check = await self.repository.get_by_id(lesson_id)
        if not lesson_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id = {lesson_id} is not found",
            )
        update_dict = lesson_data.model_dump(exclude_unset=True)
        lesson = await self.repository.update(lesson_id, update_dict)
        if not lesson:
            # на случай, если обновление не удалось (хотя проверка выше есть)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id = {lesson_id} not found during update",
            )
        return LessonResponse.model_validate(lesson)

    async def delete_lesson(self, lesson_id: int) -> bool:
        lesson_exist_check = await self.repository.get_by_id(lesson_id)
        if not lesson_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id = {lesson_id} is not found",
            )
        result = await self.repository.delete(lesson_id)
        return result

    async def get_lessons_by_week(self, week_id: int) -> List[LessonResponse]:
        """Получить все уроки определённой недели, отсортированные по порядку"""
        lessons = await self.repository.get_by_week_id(week_id)
        return [LessonResponse.model_validate(lesson) for lesson in lessons]

    async def get_lessons_count(self) -> int:
        """Получить общее количество уроков"""
        return await self.repository.get_count()