from sqlalchemy.orm import Session
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.repositories.word_repository import WordRepository
from app.schemas.word import (
    WordCreate,
    WordResponse,
    WordUpdate,
    WordWithLessonsResponse,
)


class WordService:
    def __init__(self, db: Session):
        self.repository = WordRepository(db)

    def get_all_words(self) -> List[WordResponse]:
        words = self.repository.get_all()
        return [WordResponse.model_validate(word) for word in words]

    def get_word_by_id(self, word_id: int) -> WordResponse:
        word = self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )
        return WordResponse.model_validate(word)

    def get_word_with_lessons(self, word_id: int) -> WordWithLessonsResponse:
        """Получить слово с ID уроков, в которых оно используется"""
        word = self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )

        lesson_ids = self.repository.get_lesson_ids(word_id)

        return WordWithLessonsResponse(
            id=word.id,
            hanzi=word.hanzi,
            transcription=word.transcription,
            translation=word.translation,
            part_of_speech=word.part_of_speech,
            example_sentence=word.example_sentence,
            example_translation=word.example_translation,
            audio_url=word.audio_url,
            lesson_ids=lesson_ids,
        )

    def get_words_by_lesson(self, lesson_id: int) -> List[WordResponse]:
        """Получить все слова по ID урока"""
        words = self.repository.get_by_lesson(lesson_id)
        return [WordResponse.model_validate(word) for word in words]

    def create_word(self, word_data: WordCreate) -> WordResponse:
        word = self.repository.create(word_data.model_dump())
        return WordResponse.model_validate(word)

    def update_word(self, word_id: int, word_data: WordUpdate) -> WordResponse:
        word = self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )

        update_dict = word_data.model_dump(exclude_unset=True)
        updated_word = self.repository.update(word_id, update_dict)
        return WordResponse.model_validate(updated_word)

    def delete_word(self, word_id: int) -> Dict[str, Any]:
        word = self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )

        self.repository.delete(word_id)
        return {"message": f"Word {word_id} deleted successfully"}

    def add_word_to_lesson(self, word_id: int, lesson_id: int) -> Dict[str, Any]:
        """Добавить слово к уроку"""
        word = self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(404, f"Word {word_id} not found")

        if self.repository.add_to_lesson(word_id, lesson_id):
            return {"message": f"Word {word_id} added to lesson {lesson_id}"}
        raise HTTPException(400, "Failed to add word to lesson")

    def remove_word_from_lesson(self, word_id: int, lesson_id: int) -> Dict[str, Any]:
        """Удалить слово из урока"""
        word = self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(404, f"Word {word_id} not found")

        if self.repository.remove_from_lesson(word_id, lesson_id):
            return {"message": f"Word {word_id} removed from lesson {lesson_id}"}
        raise HTTPException(400, "Failed to remove word from lesson")
