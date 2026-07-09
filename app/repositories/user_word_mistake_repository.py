from typing import List

from sqlalchemy import select, func, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_word_mistake import UserWordMistake
from app.models.word import Word


class UserWordMistakeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_mistake(self, user_id: int, word_id: int) -> None:
        """Добавить слово в стек ошибок (без дублирования)"""
        stmt = insert(UserWordMistake).values(
            user_id=user_id, word_id=word_id
        ).on_conflict_do_nothing(constraint="uq_user_word_mistake")
        await self.db.execute(stmt)
        await self.db.commit()

    async def remove_mistake(self, user_id: int, word_id: int) -> None:
        """Убрать слово из стека ошибок"""
        stmt = delete(UserWordMistake).where(
            UserWordMistake.user_id == user_id,
            UserWordMistake.word_id == word_id,
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_mistakes(self, user_id: int) -> List[Word]:
        """Получить все слова в стеке ошибок пользователя"""
        result = await self.db.execute(
            select(UserWordMistake)
            .where(UserWordMistake.user_id == user_id)
            .order_by(UserWordMistake.added_at.desc())
        )
        mistakes = result.scalars().all()
        return [m.word for m in mistakes]

    async def get_mistake_count(self, user_id: int) -> int:
        """Получить количество слов в стеке ошибок"""
        result = await self.db.execute(
            select(func.count(UserWordMistake.id)).where(
                UserWordMistake.user_id == user_id
            )
        )
        return result.scalar_one() or 0

    async def has_mistake(self, user_id: int, word_id: int) -> bool:
        """Проверить, есть ли слово в стеке ошибок"""
        result = await self.db.execute(
            select(UserWordMistake.id).where(
                UserWordMistake.user_id == user_id,
                UserWordMistake.word_id == word_id,
            )
        )
        return result.scalar_one_or_none() is not None
