from sqlalchemy.orm import Session
from typing import List
from app.models.lesson_word_association import lesson_word_association


class LessonWordAssociationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_word_ids_by_lesson(self, lesson_id: int) -> List[int]:
        """Получить все ID слов, связанных с уроком"""
        result = self.db.execute(
            lesson_word_association.select().where(
                lesson_word_association.c.lesson_id == lesson_id
            )
        ).fetchall()
        return [row[1] for row in result]
