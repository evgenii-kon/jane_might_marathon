from datetime import date, timedelta
from typing import List

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_activity import UserActivity


class UserActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_activity(self, user_id: int, activity_date: date) -> None:
        """Увеличить активность пользователя за день на 1"""
        stmt = insert(UserActivity).values(
            user_id=user_id,
            date=activity_date,
            activity_count=1,
        ).on_conflict_do_update(
            constraint="uq_user_activity_date",
            set_={"activity_count": UserActivity.activity_count + 1},
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_activity_for_year(self, user_id: int, year: int) -> List[UserActivity]:
        """Получить активность пользователя за год"""
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        result = await self.db.execute(
            select(UserActivity)
            .where(
                UserActivity.user_id == user_id,
                UserActivity.date >= start,
                UserActivity.date <= end,
            )
            .order_by(UserActivity.date)
        )
        return result.scalars().all()

    async def get_streak(self, user_id: int) -> int:
        """Получить количество серии активных дней пользователя"""
        today = date.today()
        result = await self.db.execute(
            select(UserActivity.date)
            .where(UserActivity.user_id == user_id)
            .order_by(UserActivity.date.desc())
        )
        dates = set(result.scalars().all())

        if not dates:
            return 0

        # Allow streak if today OR yesterday has activity (so streak survives until end of day)
        cursor = today if today in dates else (today - timedelta(days=1))
        if cursor not in dates:
            return 0

        streak = 0
        while cursor in dates:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    async def get_total_active_days(self, user_id: int) -> int:
        result = await self.db.execute(
            select(UserActivity).where(UserActivity.user_id == user_id)
        )
        return len(result.scalars().all())
