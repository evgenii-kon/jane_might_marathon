from datetime import date, timedelta
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_activity_repository import UserActivityRepository


class UserActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserActivityRepository(db)

    async def record_activity(self, user_id: int) -> None:
        await self.repository.upsert_activity(user_id, date.today())

    async def get_year_activity(self, user_id: int, year: int | None = None) -> Dict[str, int]:
        if year is None:
            year = date.today().year
        records = await self.repository.get_activity_for_year(user_id, year)
        return {str(r.date): r.activity_count for r in records}

    async def get_streak(self, user_id: int) -> int:
        return await self.repository.get_streak(user_id)

    async def get_total_active_days(self, user_id: int) -> int:
        return await self.repository.get_total_active_days(user_id)
