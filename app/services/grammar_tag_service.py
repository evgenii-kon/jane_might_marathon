from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException, status
from ..repositories.grammar_tag_repository import GrammarTagRepository
from ..schemas.grammar import GrammarTagCreate, GrammarTagResponse
from ..services.cashe_service import CacheService


class GrammarTagService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = GrammarTagRepository(db)
        self.cache = CacheService(prefix="grammar_tags", ttl=600)

    async def get_all_tags(self) -> List[GrammarTagResponse]:
        cached = await self.cache.get("all")
        if cached:
            return [GrammarTagResponse.model_validate(t) for t in cached]
        tags = await self.repository.get_all()
        result = [GrammarTagResponse.model_validate(t) for t in tags]
        await self.cache.set([t.model_dump(mode="json") for t in result], "all")
        return result

    async def get_tag_by_id(self, tag_id: int) -> GrammarTagResponse:
        tag = await self.repository.get_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with id={tag_id} not found",
            )
        return GrammarTagResponse.model_validate(tag)

    async def get_tag_by_slug(self, slug: str) -> GrammarTagResponse:
        tag = await self.repository.get_by_slug(slug)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with slug='{slug}' not found",
            )
        return GrammarTagResponse.model_validate(tag)

    async def create_tag(self, data: GrammarTagCreate) -> GrammarTagResponse:
        existing = await self.repository.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with slug='{data.slug}' already exists",
            )
        await self.cache.delete_pattern("*")
        tag = await self.repository.create(data.name, data.slug)
        return GrammarTagResponse.model_validate(tag)

    async def delete_tag(self, tag_id: int) -> None:
        tag = await self.repository.get_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with id={tag_id} not found",
            )
        await self.cache.delete_pattern("*")
        await self.repository.delete(tag_id)
