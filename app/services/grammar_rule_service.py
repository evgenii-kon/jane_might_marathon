from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException, status
from ..repositories.grammar_rule_repository import GrammarRuleRepository
from ..repositories.grammar_tag_repository import GrammarTagRepository
from ..schemas.grammar import GrammarRuleCreate, GrammarRuleUpdate, GrammarRuleResponse
from ..services.cashe_service import CacheService


class GrammarRuleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = GrammarRuleRepository(db)
        self.tag_repository = GrammarTagRepository(db)
        self.cache = CacheService(prefix="grammar", ttl=600)

    async def get_all_rules(self) -> List[GrammarRuleResponse]:
        cached = await self.cache.get("all")
        if cached:
            return [GrammarRuleResponse.model_validate(r) for r in cached]
        rules = await self.repository.get_all()
        result = [GrammarRuleResponse.model_validate(r) for r in rules]
        await self.cache.set([r.model_dump(mode="json") for r in result], "all")
        return result

    async def get_rule_by_id(self, rule_id: int) -> GrammarRuleResponse:
        cached = await self.cache.get("id", rule_id)
        if cached:
            return GrammarRuleResponse.model_validate(cached)
        rule = await self.repository.get_by_id(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grammar rule with id={rule_id} not found",
            )
        result = GrammarRuleResponse.model_validate(rule)
        await self.cache.set(result.model_dump(mode="json"), "id", rule_id)
        return result

    async def get_rule_by_slug(self, slug: str) -> GrammarRuleResponse:
        cached = await self.cache.get("slug", slug)
        if cached:
            return GrammarRuleResponse.model_validate(cached)
        rule = await self.repository.get_by_slug(slug)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grammar rule with slug='{slug}' not found",
            )
        result = GrammarRuleResponse.model_validate(rule)
        await self.cache.set(result.model_dump(mode="json"), "slug", slug)
        return result

    async def get_rules_by_tag(self, tag_slug: str) -> List[GrammarRuleResponse]:
        cached = await self.cache.get("tag", tag_slug)
        if cached:
            return [GrammarRuleResponse.model_validate(r) for r in cached]
        rules = await self.repository.get_by_tag(tag_slug)
        result = [GrammarRuleResponse.model_validate(r) for r in rules]
        await self.cache.set([r.model_dump(mode="json") for r in result], "tag", tag_slug)
        return result

    async def create_rule(self, data: GrammarRuleCreate) -> GrammarRuleResponse:
        existing = await self.repository.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Grammar rule with slug='{data.slug}' already exists",
            )
        tags = await self.tag_repository.get_by_ids(data.tag_ids)
        await self.cache.delete_pattern("*")
        rule = await self.repository.create(
            title=data.title,
            slug=data.slug,
            content=data.content,
            description=data.description,
            hsk_level=data.hsk_level,
            tags=tags,
        )
        return GrammarRuleResponse.model_validate(rule)

    async def update_rule(self, rule_id: int, data: GrammarRuleUpdate) -> GrammarRuleResponse:
        rule = await self.repository.get_by_id(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grammar rule with id={rule_id} not found",
            )
        if data.slug and data.slug != rule.slug:
            existing = await self.repository.get_by_slug(data.slug)
            if existing and existing.id != rule_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Grammar rule with slug='{data.slug}' already exists",
                )
        tags: Optional[List] = None
        if data.tag_ids is not None:
            tags = await self.tag_repository.get_by_ids(data.tag_ids)

        update_dict = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        await self.cache.delete_pattern("*")
        updated = await self.repository.update(rule_id, update_dict, tags)
        return GrammarRuleResponse.model_validate(updated)

    async def delete_rule(self, rule_id: int) -> None:
        rule = await self.repository.get_by_id(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grammar rule with id={rule_id} not found",
            )
        await self.cache.delete_pattern("*")
        await self.repository.delete(rule_id)
