from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_idiom_progress_repository import UserIdiomProgressRepository

VALID_STATUSES = {"not_known", "learning", "known"}


class UserIdiomProgressService:
    def __init__(self, db: AsyncSession):
        self.repository = UserIdiomProgressRepository(db)

    async def get_status(self, user_id: int, idiom_id: int) -> str:
        progress = await self.repository.get(user_id, idiom_id)
        return progress.status if progress else "not_known"

    async def set_status(self, user_id: int, idiom_id: int, status_value: str) -> str:
        if status_value not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_value}'",
            )
        progress = await self.repository.set_status(user_id, idiom_id, status_value)
        return progress.status
