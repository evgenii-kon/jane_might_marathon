from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException, status
from ..repositories.week_repository import WeekRepository
from ..schemas.week import WeekCreate, WeekResponse, WeekUpdate
from ..models.week import Week
from ..services.cashe_service import CacheService


class WeekService:
    def __init__(self, db: AsyncSession):
        self.repository = WeekRepository(db)
        self.cache = CacheService(prefix="weeks", ttl=600)

    async def _get_existing_week(self, week_id: int) -> Week:
        week = await self.repository.get_by_id(week_id)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week with id={week_id} not found",
            )
        return week

    async def _check_unique_slug(self, new_slug: str | None, old_slug: str) -> None:
        if new_slug and new_slug != old_slug:
            slug_exists = await self.repository.get_by_slug(new_slug)
            if slug_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Week with slug={new_slug} already exists",
                )

    async def _check_unique_number(self, new_number: int | None, old_number: int) -> None:
        if new_number and new_number != old_number:
            number_exists = await self.repository.get_by_number(new_number)
            if number_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Week with number={new_number} already exists",
                )

    async def get_all_weeks(self) -> List[WeekResponse]:
        cached = await self.cache.get("all")
        if cached:
            return [WeekResponse.model_validate(w) for w in cached]

        weeks = await self.repository.get_all()
        result = [WeekResponse.model_validate(week) for week in weeks]
        await self.cache.set([w.model_dump(mode='json') for w in result], "all")
        return result

    async def get_week_by_id(self, week_id: int) -> WeekResponse:
        cached = await self.cache.get("id", week_id)
        if cached:
            return WeekResponse.model_validate(cached)

        week = await self.repository.get_by_id(week_id)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week with id={week_id} not found",
            )
        result = WeekResponse.model_validate(week)
        await self.cache.set(result.model_dump(mode='json'), "id", week_id)
        return result

    async def get_week_by_slug(self, slug: str) -> WeekResponse:
        cached = await self.cache.get("slug", slug)
        if cached:
            return WeekResponse.model_validate(cached)

        week = await self.repository.get_by_slug(slug)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week with slug={slug} not found",
            )
        result = WeekResponse.model_validate(week)
        await self.cache.set(result.model_dump(mode='json'), "slug", slug)
        return result

    async def get_week_by_number(self, number: int) -> WeekResponse:
        cached = await self.cache.get("number", number)
        if cached:
            return WeekResponse.model_validate(cached)

        week = await self.repository.get_by_number(number)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week with number={number} not found",
            )
        result = WeekResponse.model_validate(week)
        await self.cache.set(result.model_dump(mode='json'), "number", number)
        return result

    async def create_week(self, week_data: WeekCreate) -> WeekResponse:
        slug_exists = await self.repository.get_by_slug(week_data.slug)
        if slug_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Week with slug={week_data.slug} already exists",
            )

        number_exists = await self.repository.get_by_number(week_data.number)
        if number_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Week with number={week_data.number} already exists",
            )

        await self.cache.delete_pattern("*")
        new_week = await self.repository.create(week_data)
        return WeekResponse.model_validate(new_week)

    async def update_week(self, week_id: int, week_data: WeekUpdate) -> WeekResponse:
        existing_week = await self._get_existing_week(week_id)
        await self._check_unique_slug(week_data.slug, existing_week.slug)
        await self._check_unique_number(week_data.number, existing_week.number)

        await self.cache.delete_pattern("*")
        update_dict = week_data.model_dump(exclude_unset=True)
        updated_week = await self.repository.update(week_id, update_dict)
        return WeekResponse.model_validate(updated_week)

    async def delete_week(self, week_id: int) -> bool:
        existing_week = await self.repository.get_by_id(week_id)
        if not existing_week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Week with id={week_id} not found",
            )
        await self.cache.delete_pattern("*")
        return await self.repository.delete(week_id)