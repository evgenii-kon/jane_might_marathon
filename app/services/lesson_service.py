from sqlalchemy.orm import Session
from typing import List
from ..repositories.lesson_repository import LessonRepository
from ..schemas.lesson import LessonCreate, LessonResponse, LessonUpdate
from fastapi import status, HTTPException


class LessonService:
    def __init__(self, db: Session):
        self.repository = LessonRepository(db)

    def get_all_lessons(self) -> List[LessonResponse]:
        lessons = self.repository.get_all()
        return [LessonResponse.model_validate(lesson) for lesson in lessons]

    def get_lesson_by_id(self, lesson_id: int) -> LessonResponse:
        lesson = self.repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"lesson with id={lesson_id} not found",
            )
        return LessonResponse.model_validate(lesson)

    def create_lesson(self, lesson_data: LessonCreate) -> LessonResponse:
        lesson_exist_check = self.repository.get_by_name(lesson_data.name)
        if lesson_exist_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lesson with name {lesson_data.name} is already exist",
            )
        new_lesson = self.repository.create(lesson_data)
        return LessonResponse.model_validate(new_lesson)

    def update_lesson(
        self, lesson_id: int, lesson_data: LessonUpdate
    ) -> LessonResponse:
        lesson_exist_check = self.repository.get_by_id(lesson_id)
        if not lesson_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id = {lesson_id} is not found",
            )
        update_dict = lesson_data.model_dump(exclude_unset=True)
        lesson = self.repository.update(lesson_id, update_dict)

        return LessonResponse.model_validate(lesson)

    def delete_lesson(self, lesson_id: int) -> bool:
        lesson_exist_check = self.repository.get_by_id(lesson_id)
        if not lesson_exist_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id = {lesson_id} is not found",
            )
        lesson = self.repository.delete(lesson_id)
        return lesson

    def get_lessons_by_week(self, week_id: int) -> List[LessonResponse]:
        """Получить все уроки определённой недели, отсортированные по порядку"""
        lessons = self.repository.get_by_week_id(week_id)
        return [LessonResponse.model_validate(lesson) for lesson in lessons]

    def get_lessons_count(self) -> int:
        """Получить общее количество уроков"""
        return self.repository.get_count()
