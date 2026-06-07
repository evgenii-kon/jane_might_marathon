from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException, status

from ..repositories.idiom_repository import IdiomRepository
from ..schemas.idiom import IdiomCreate, IdiomUpdate, IdiomResponse
from ..services.cashe_service import CacheService


class IdiomService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = IdiomRepository(db)
        self.cache = CacheService(prefix="idioms", ttl=600)

    async def get_all_idioms(self) -> List[IdiomResponse]:
        cached = await self.cache.get("all")
        if cached:
            return [IdiomResponse.model_validate(i) for i in cached]

        idioms = await self.repository.get_all()
        result = [IdiomResponse.model_validate(i) for i in idioms]
        await self.cache.set([i.model_dump(mode="json") for i in result], "all")
        return result

    async def get_idiom_by_id(self, idiom_id: int) -> IdiomResponse:
        cached = await self.cache.get("id", idiom_id)
        if cached:
            return IdiomResponse.model_validate(cached)

        idiom = await self.repository.get_by_id(idiom_id)
        if not idiom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idiom with id={idiom_id} not found",
            )
        result = IdiomResponse.model_validate(idiom)
        await self.cache.set(result.model_dump(mode="json"), "id", idiom_id)
        return result

    async def create_idiom(self, idiom_data: IdiomCreate) -> IdiomResponse:
        await self.cache.delete_pattern("*")
        new_idiom = await self.repository.create(idiom_data)
        return IdiomResponse.model_validate(new_idiom)

    async def update_idiom(self, idiom_id: int, idiom_data: IdiomUpdate) -> IdiomResponse:
        idiom = await self.repository.get_by_id(idiom_id)
        if not idiom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idiom with id={idiom_id} not found",
            )
        await self.cache.delete_pattern("*")
        update_dict = idiom_data.model_dump(exclude_unset=True)
        updated = await self.repository.update(idiom_id, update_dict)
        return IdiomResponse.model_validate(updated)

    async def delete_idiom(self, idiom_id: int) -> None:
        idiom = await self.repository.get_by_id(idiom_id)
        if not idiom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idiom with id={idiom_id} not found",
            )
        await self.cache.delete_pattern("*")
        await self.repository.delete(idiom_id)

    async def get_idioms_count(self) -> int:
        return await self.repository.count()
