from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.repositories.word_repository import WordRepository
from app.schemas.word import (
    WordCreate,
    WordResponse,
    WordUpdate,
    WordWithLessonsResponse,
)
from app.services.cashe_service import CacheService


class WordService:
    def __init__(self, db: AsyncSession):
        self.repository = WordRepository(db)
        self.cache = CacheService(prefix="words", ttl=600)

    async def get_all_words(self) -> List[WordResponse]:
        cached = await self.cache.get("all")
        if cached:
            return [WordResponse.model_validate(w) for w in cached]

        words = await self.repository.get_all()
        result = [WordResponse.model_validate(word) for word in words]
        await self.cache.set([w.model_dump() for w in result], "all")
        return result

    async def get_word_by_id(self, word_id: int) -> WordResponse:
        cached = await self.cache.get("id", word_id)
        if cached:
            return WordResponse.model_validate(cached)

        word = await self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )
        result = WordResponse.model_validate(word)
        await self.cache.set(result.model_dump(), "id", word_id)
        return result

    async def get_word_with_lessons(self, word_id: int) -> WordWithLessonsResponse:
        """Получить слово с ID уроков, в которых оно используется"""
        cached = await self.cache.get("with_lessons", word_id)
        if cached:
            return WordWithLessonsResponse.model_validate(cached)

        word = await self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )

        lesson_ids = await self.repository.get_lesson_ids(word_id)

        result = WordWithLessonsResponse(
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
        await self.cache.set(result.model_dump(), "with_lessons", word_id)
        return result

    async def get_words_by_lesson(self, lesson_id: int) -> List[WordResponse]:
        """Получить все слова по ID урока"""
        cached = await self.cache.get("lesson", lesson_id)
        if cached:
            return [WordResponse.model_validate(w) for w in cached]

        words = await self.repository.get_by_lesson(lesson_id)
        result = [WordResponse.model_validate(word) for word in words]
        await self.cache.set([w.model_dump() for w in result], "lesson", lesson_id)
        return result

    async def create_word(self, word_data: WordCreate) -> WordResponse:
        await self.cache.delete_pattern("*")
        word = await self.repository.create(word_data.model_dump())
        return WordResponse.model_validate(word)

    async def update_word(self, word_id: int, word_data: WordUpdate) -> WordResponse:
        word = await self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )

        await self.cache.delete_pattern("*")
        update_dict = word_data.model_dump(exclude_unset=True)
        updated_word = await self.repository.update(word_id, update_dict)
        return WordResponse.model_validate(updated_word)

    async def delete_word(self, word_id: int) -> Dict[str, Any]:
        word = await self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word with id {word_id} not found",
            )

        await self.cache.delete_pattern("*")
        await self.repository.delete(word_id)
        return {"message": f"Word {word_id} deleted successfully"}

    async def add_word_to_lesson(self, word_id: int, lesson_id: int) -> Dict[str, Any]:
        """Добавить слово к уроку"""
        word = await self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(404, f"Word {word_id} not found")

        if await self.repository.add_to_lesson(word_id, lesson_id):
            await self.cache.delete_pattern("*")
            return {"message": f"Word {word_id} added to lesson {lesson_id}"}
        raise HTTPException(400, "Failed to add word to lesson")

    async def remove_word_from_lesson(self, word_id: int, lesson_id: int) -> Dict[str, Any]:
        """Удалить слово из урока"""
        word = await self.repository.get_by_id(word_id)
        if not word:
            raise HTTPException(404, f"Word {word_id} not found")

        if await self.repository.remove_from_lesson(word_id, lesson_id):
            await self.cache.delete_pattern("*")
            return {"message": f"Word {word_id} removed from lesson {lesson_id}"}
        raise HTTPException(400, "Failed to remove word from lesson")