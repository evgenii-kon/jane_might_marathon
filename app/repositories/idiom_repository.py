from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from ..models.idiom import Idiom
from ..schemas.idiom import IdiomCreate


class IdiomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Idiom]:
        result = await self.db.execute(
            select(Idiom).order_by(Idiom.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, idiom_id: int) -> Optional[Idiom]:
        result = await self.db.execute(
            select(Idiom).where(Idiom.id == idiom_id)
        )
        return result.scalar_one_or_none()

    async def create(self, idiom_data: IdiomCreate) -> Idiom:
        new_idiom = Idiom(**idiom_data.model_dump())
        self.db.add(new_idiom)
        await self.db.commit()
        await self.db.refresh(new_idiom)
        return new_idiom

    async def update(self, idiom_id: int, update_data: dict) -> Optional[Idiom]:
        idiom = await self.get_by_id(idiom_id)
        if not idiom:
            return None
        for key, value in update_data.items():
            setattr(idiom, key, value)
        await self.db.commit()
        await self.db.refresh(idiom)
        return idiom

    async def delete(self, idiom_id: int) -> bool:
        idiom = await self.get_by_id(idiom_id)
        if not idiom:
            return False
        await self.db.delete(idiom)
        await self.db.commit()
        return True

    async def count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Idiom))
        return result.scalar_one()
