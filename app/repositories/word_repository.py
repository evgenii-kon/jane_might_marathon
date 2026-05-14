from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.word import Word
from app.models.lesson import Lesson




class WordRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[Word]:
        return self.db.query(Word).all()


    def get_by_id(self, word_id: int) -> Optional[Word]:
        return self.db.query(Word).filter(Word.id == word_id).first()


    def get_by_ids(self, word_ids: List[int]) -> List[Word]:
        """Получить несколько слов по списку ID"""
        if not word_ids:
            return []
        return self.db.query(Word).filter(Word.id.in_(word_ids)).all()


    def get_by_lesson(self, lesson_id: int) -> List[Word]:
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        return lesson.words if lesson else []


    def get_lesson_ids(self, word_id: int) -> List[int]:
        word = self.get_by_id(word_id)
        if not word:
            return []
        return [lesson.id for lesson in word.lessons]


    def create(self, word_data: dict) -> Word:
        word = Word(**word_data)
        self.db.add(word)
        self.db.commit()
        self.db.refresh(word)
        return word


    def update(self, word_id: int, update_data: dict) -> Optional[Word]:
        word = self.get_by_id(word_id)
        if not word:
            return None
        
        for key, value in update_data.items():
            setattr(word, key, value)
        
        self.db.commit()
        self.db.refresh(word)
        return word


    def delete(self, word_id: int) -> bool:
        word = self.get_by_id(word_id)
        if word:
            self.db.delete(word)
            self.db.commit()
            return True
        return False


    def add_to_lesson(self, word_id: int, lesson_id: int) -> bool:
        word = self.get_by_id(word_id)
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        
        if not word or not lesson:
            return False
        
        if word not in lesson.words:
            lesson.words.append(word)
            self.db.commit()
        return True


    def remove_from_lesson(self, word_id: int, lesson_id: int) -> bool:
        from app.models.lesson import Lesson
        word = self.get_by_id(word_id)
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        
        if not word or not lesson:
            return False
        
        if word in lesson.words:
            lesson.words.remove(word)
            self.db.commit()
        return True