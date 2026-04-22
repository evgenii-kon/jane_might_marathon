from sqlalchemy.orm import Session
from typing import List
from ..repositories.week_repository import WeekRepository
from ..schemas.week import WeekCreate, WeekResponse, WeekUpdate
from fastapi import status, HTTPException
from ..models.week import Week


class WeekService:
    def __init__(self, db: Session):
        self.repository = WeekRepository(db)


        # Приватные методы для проверок
    def _get_existing_week(self, week_id: int) -> Week:
        week = self.repository.get_by_id(week_id)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Week with id={week_id} not found'
            )
        return week
    

    def _check_unique_slug(self, new_slug: str | None, old_slug: str) -> None:
        if new_slug and new_slug != old_slug:
            slug_exists = self.repository.get_by_slug(new_slug)
            if slug_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Week with slug={new_slug} already exists'
                )


    def _check_unique_number(self, new_number: int | None, old_number: int) -> None:
        if new_number and new_number != old_number:
            number_exists = self.repository.get_by_number(new_number)
            if number_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Week with number={new_number} already exists'
                )


    def get_all_weeks(self) -> List[WeekResponse]:
        weeks = self.repository.get_all()
        return [WeekResponse.model_validate(week) for week in weeks]


    def get_week_by_id(self, week_id: int) -> WeekResponse:
        week = self.repository.get_by_id(week_id)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Week with id={week_id} not found'
            )
        return WeekResponse.model_validate(week)


    def get_week_by_slug(self, slug: str) -> WeekResponse:
        week = self.repository.get_by_slug(slug)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Week with slug={slug} not found'
            )
        return WeekResponse.model_validate(week)


    def get_week_by_number(self, number: int) -> WeekResponse:
        week = self.repository.get_by_number(number)
        if not week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Week with number={number} not found'
            )
        return WeekResponse.model_validate(week)


    def create_week(self, week_data: WeekCreate) -> WeekResponse:
        slug_exists = self.repository.get_by_slug(week_data.slug)
        if slug_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Week with slug={week_data.slug} already exists'
            )
        
        number_exists = self.repository.get_by_number(week_data.number)
        if number_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Week with number={week_data.number} already exists'
            )
        
        new_week = self.repository.create(week_data)
        return WeekResponse.model_validate(new_week)


    def update_week(self, week_id: int, week_data: WeekUpdate) -> WeekResponse:
        existing_week = self._get_existing_week(week_id)
        self._check_unique_slug(week_data.slug, existing_week.slug)
        self._check_unique_number(week_data.number, existing_week.number)
        
        update_dict = week_data.model_dump(exclude_unset=True)
        updated_week = self.repository.update(week_id, update_dict)
        return WeekResponse.model_validate(updated_week)


    def delete_week(self, week_id: int) -> bool:
        existing_week = self.repository.get_by_id(week_id)
        if not existing_week:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Week with id={week_id} not found'
            )
        return self.repository.delete(week_id)