from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from ..models.grammar_tag import GrammarTag


class GrammarTagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[GrammarTag]:
        result = await self.db.execute(select(GrammarTag).order_by(GrammarTag.name))
        return result.scalars().all()

    async def get_by_id(self, tag_id: int) -> Optional[GrammarTag]:
        result = await self.db.execute(select(GrammarTag).where(GrammarTag.id == tag_id))
        return result.scalar_one_or_none()

    async def get_by_ids(self, tag_ids: List[int]) -> List[GrammarTag]:
        if not tag_ids:
            return []
        result = await self.db.execute(select(GrammarTag).where(GrammarTag.id.in_(tag_ids)))
        return result.scalars().all()

    async def get_by_slug(self, slug: str) -> Optional[GrammarTag]:
        result = await self.db.execute(select(GrammarTag).where(GrammarTag.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, name: str, slug: str) -> GrammarTag:
        tag = GrammarTag(name=name, slug=slug)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def delete(self, tag_id: int) -> bool:
        tag = await self.get_by_id(tag_id)
        if not tag:
            return False
        await self.db.delete(tag)
        await self.db.commit()
        return True
