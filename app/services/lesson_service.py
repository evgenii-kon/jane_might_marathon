from sqlalchemy.orm import Session
from typing import List
from ..repositories.lesson_repository import LessonRepository
from ..schemas.lesson import LessonCreate, LessonResponse
from ..models.lesson import Lesson
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
                detail=f'lesson with id={lesson_id} not found'
            )
        return [LessonResponse.model_validate(lesson)]
    

    def create(self, lesson_data: LessonCreate) -> LessonResponse:
        new_lesson = self.repository.create(lesson_data)
        return LessonResponse.model_validate(new_lesson)
    
    