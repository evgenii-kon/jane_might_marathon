from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from ..models.week import Week
from ..schemas.week import WeekCreate


class WeekRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Week]:
        result = await self.db.execute(select(Week).order_by(Week.id.asc()))
        return result.scalars().all()

    async def get_by_id(self, week_id: int) -> Optional[Week]:
        result = await self.db.execute(select(Week).where(Week.id == week_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Week]:
        result = await self.db.execute(select(Week).where(Week.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_number(self, number: int) -> Optional[Week]:
        result = await self.db.execute(select(Week).where(Week.number == number))
        return result.scalar_one_or_none()

    async def create(self, week_data: WeekCreate) -> Week:
        new_week = Week(**week_data.model_dump())
        self.db.add(new_week)
        await self.db.commit()
        await self.db.refresh(new_week)
        return new_week

    async def update(self, week_id: int, update_data: dict) -> Optional[Week]:
        week = await self.get_by_id(week_id)
        if not week:
            return None
        for key, value in update_data.items():
            setattr(week, key, value)
        await self.db.commit()
        await self.db.refresh(week)
        return week

    async def delete(self, week_id: int) -> bool:
        week = await self.get_by_id(week_id)
        if week:
            await self.db.delete(week)
            await self.db.commit()
            return True
        return False