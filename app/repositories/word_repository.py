from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List, Optional
from app.models.word import Word
from app.models.lesson_word_association import lesson_word_association


class WordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_random(self) -> Optional[Word]:
        result = await self.db.execute(select(Word).order_by(func.random()).limit(1))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Word]:
        result = await self.db.execute(select(Word))
        return result.scalars().all()

    async def get_by_id(self, word_id: int) -> Optional[Word]:
        result = await self.db.execute(select(Word).where(Word.id == word_id))
        return result.scalar_one_or_none()

    async def get_by_ids(self, word_ids: List[int]) -> List[Word]:
        """Получить несколько слов по списку ID"""
        if not word_ids:
            return []
        result = await self.db.execute(select(Word).where(Word.id.in_(word_ids)))
        return result.scalars().all()

    async def get_by_lesson(self, lesson_id: int) -> List[Word]:
        """Получить слова, связанные с уроком, через ассоциативную таблицу"""
        result = await self.db.execute(
            select(Word)
            .join(lesson_word_association, Word.id == lesson_word_association.c.word_id)
            .where(lesson_word_association.c.lesson_id == lesson_id)
        )
        return result.scalars().all()

    async def get_lesson_ids(self, word_id: int) -> List[int]:
        """Получить ID уроков, в которых используется слово"""
        result = await self.db.execute(
            select(lesson_word_association.c.lesson_id)
            .where(lesson_word_association.c.word_id == word_id)
        )
        return result.scalars().all()

    async def create(self, word_data: dict) -> Word:
        word = Word(**word_data)
        self.db.add(word)
        await self.db.commit()
        await self.db.refresh(word)
        return word

    async def update(self, word_id: int, update_data: dict) -> Optional[Word]:
        word = await self.get_by_id(word_id)
        if not word:
            return None
        for key, value in update_data.items():
            setattr(word, key, value)
        await self.db.commit()
        await self.db.refresh(word)
        return word

    async def delete(self, word_id: int) -> bool:
        word = await self.get_by_id(word_id)
        if word:
            await self.db.delete(word)
            await self.db.commit()
            return True
        return False

    async def add_to_lesson(self, word_id: int, lesson_id: int) -> bool:
        """Добавить слово в урок (создать запись в ассоциации)"""
        # Проверяем, существует ли уже связь
        result = await self.db.execute(
            select(lesson_word_association).where(
                lesson_word_association.c.word_id == word_id,
                lesson_word_association.c.lesson_id == lesson_id,
            )
        )
        if result.first():
            return True  # уже есть

        # Вставляем новую связь
        stmt = lesson_word_association.insert().values(word_id=word_id, lesson_id=lesson_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def remove_from_lesson(self, word_id: int, lesson_id: int) -> bool:
        """Удалить слово из урока"""
        stmt = delete(lesson_word_association).where(
            lesson_word_association.c.word_id == word_id,
            lesson_word_association.c.lesson_id == lesson_id,
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0