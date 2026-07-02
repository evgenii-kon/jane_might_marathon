from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException, status

from ..repositories.reading_text_repository import ReadingTextRepository
from ..schemas.reading import ReadingTextCreate, ReadingTextUpdate, ReadingTextResponse
from ..services.cashe_service import CacheService


class ReadingTextService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReadingTextRepository(db)
        self.cache = CacheService(prefix="reading", ttl=600)

    async def get_all(self) -> List[ReadingTextResponse]:
        cached = await self.cache.get("all")
        if cached:
            return [ReadingTextResponse.model_validate(t) for t in cached]
        texts = await self.repository.get_all()
        result = [ReadingTextResponse.model_validate(t) for t in texts]
        await self.cache.set([t.model_dump(mode="json") for t in result], "all")
        return result

    async def get_by_id(self, text_id: int) -> ReadingTextResponse:
        cached = await self.cache.get("id", text_id)
        if cached:
            return ReadingTextResponse.model_validate(cached)
        obj = await self.repository.get_by_id(text_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reading text {text_id} not found")
        result = ReadingTextResponse.model_validate(obj)
        await self.cache.set(result.model_dump(mode="json"), "id", text_id)
        return result

    async def get_by_slug(self, slug: str) -> ReadingTextResponse:
        cached = await self.cache.get("slug", slug)
        if cached:
            return ReadingTextResponse.model_validate(cached)
        obj = await self.repository.get_by_slug(slug)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reading text '{slug}' not found")
        result = ReadingTextResponse.model_validate(obj)
        await self.cache.set(result.model_dump(mode="json"), "slug", slug)
        return result

    async def create(self, data: ReadingTextCreate) -> ReadingTextResponse:
        existing = await self.repository.get_by_slug(data.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Slug '{data.slug}' already exists")
        await self.cache.delete_pattern("*")
        obj = await self.repository.create(data)
        return ReadingTextResponse.model_validate(obj)

    async def update(self, text_id: int, data: ReadingTextUpdate) -> ReadingTextResponse:
        obj = await self.repository.get_by_id(text_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reading text {text_id} not found")
        if data.slug and data.slug != obj.slug:
            existing = await self.repository.get_by_slug(data.slug)
            if existing and existing.id != text_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Slug '{data.slug}' already exists")
        await self.cache.delete_pattern("*")
        update_dict = data.model_dump(exclude_unset=True)
        updated = await self.repository.update(text_id, update_dict)
        return ReadingTextResponse.model_validate(updated)

    async def delete(self, text_id: int) -> None:
        obj = await self.repository.get_by_id(text_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reading text {text_id} not found")
        await self.cache.delete_pattern("*")
        await self.repository.delete(text_id)
