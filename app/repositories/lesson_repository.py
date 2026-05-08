from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.lesson import Lesson
from ..schemas.lesson import LessonCreate, LessonResponse


class LessonRepository:
    def __init__(self, db: Session):
        self.db = db

    
    def get_all(self) -> List[Lesson]:
        return self.db.query(Lesson).all()
    

    def get_by_id(self, lesson_id: int) -> Optional[Lesson]:
        return self.db.query(Lesson).filter(Lesson.id==lesson_id).first()
    

    def get_by_name(self, lesson_name: str) -> Optional[Lesson]:
        return self.db.query(Lesson).filter(Lesson.name==lesson_name).first()
    

    def create(self, lesson_data: LessonCreate) -> Lesson:
        new_lesson = Lesson(**lesson_data.model_dump())
        self.db.add(new_lesson)
        self.db.commit()
        self.db.refresh(new_lesson)
        return new_lesson
    

    def update(self, lesson_id: int, update_data: dict) -> Optional[Lesson]:
        lesson = self.get_by_id(lesson_id)
        if not lesson:
            return None
        
        for key, value in update_data.items():
            setattr(lesson, key, value)

        self.db.commit()
        self.db.refresh(lesson)
        return lesson


    def delete(self, lesson_id: int) -> bool:
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if lesson:
            self.db.delete(lesson)
            self.db.commit()
            return True
        else:
            return False
        
        
    def get_by_week_id(self, week_id: int) -> List[Lesson]:
        """Получить все уроки недели, отсортированные по порядку"""
        return self.db.query(Lesson).filter(
            Lesson.week_id == week_id
        ).order_by(Lesson.order_in_week).all()
    

    def get_count(self) -> int:
        """Получить общее количество уроков"""
        return self.db.query(Lesson).count()