from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.user_novel_progress_repository import UserNovelProgressRepository


class UserNovelProgressService:
    """Сервис для отслеживания того, видел ли пользователь новеллу перед уроком"""

    def __init__(self, db: AsyncSession):
        self.repository = UserNovelProgressRepository(db)

    async def has_seen(self, user_id: int, lesson_id: int) -> bool:
        return await self.repository.has_seen(user_id, lesson_id)

    async def mark_seen(self, user_id: int, lesson_id: int) -> None:
        await self.repository.mark_seen(user_id, lesson_id)
