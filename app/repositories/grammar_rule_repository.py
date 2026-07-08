from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from ..models.grammar_rule import GrammarRule
from ..models.grammar_tag import GrammarTag


class GrammarRuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_query(self):
        return select(GrammarRule).options(selectinload(GrammarRule.tags))

    async def get_all(self) -> List[GrammarRule]:
        """Получить все правила (отсортированные по тегу в порядке убывания)"""
        result = await self.db.execute(
            self._base_query().order_by(GrammarRule.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, rule_id: int) -> Optional[GrammarRule]:
        """Получить правило по id правила"""
        result = await self.db.execute(
            self._base_query().where(GrammarRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[GrammarRule]:
        """Получить правило по slug"""
        result = await self.db.execute(
            self._base_query().where(GrammarRule.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_tag(self, tag_slug: str) -> List[GrammarRule]:
        result = await self.db.execute(
            self._base_query()
            .join(GrammarRule.tags)
            .where(GrammarTag.slug == tag_slug)
            .order_by(GrammarRule.created_at.desc())
        )
        return result.scalars().all()

    async def create(
        self,
        title: str,
        slug: str,
        content: str,
        description: Optional[str],
        hsk_level: Optional[str],
        tags: List[GrammarTag],
    ) -> GrammarRule:
        """Создать правило"""
        rule = GrammarRule(
            title=title,
            slug=slug,
            content=content,
            description=description,
            hsk_level=hsk_level,
        )
        rule.tags = tags
        self.db.add(rule)
        await self.db.commit()
        return await self.get_by_id(rule.id)

    async def update(
        self,
        rule_id: int,
        update_data: dict,
        tags: Optional[List[GrammarTag]] = None,
    ) -> Optional[GrammarRule]:
        """Обновить правило"""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return None
        for key, value in update_data.items():
            setattr(rule, key, value)
        if tags is not None:
            rule.tags = tags
        await self.db.commit()
        return await self.get_by_id(rule_id)

    async def delete(self, rule_id: int) -> bool:
        """Удалить правило"""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return False
        await self.db.delete(rule)
        await self.db.commit()
        return True
