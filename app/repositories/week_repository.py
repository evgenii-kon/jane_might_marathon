from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.week import Week
from ..schemas.week import WeekCreate, WeekResponse


class WeekRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[Week]:
        return self.db.query(Week).all()


    def get_by_id(self, week_id: int) -> Optional[Week]:
        return self.db.query(Week).filter(Week.id == week_id).first()


    def get_by_slug(self, slug: str) -> Optional[Week]:
        return self.db.query(Week).filter(Week.slug == slug).first()


    def get_by_number(self, number: int) -> Optional[Week]:
        return self.db.query(Week).filter(Week.number == number).first()


    def create(self, week_data: WeekCreate) -> Week:
        new_week = Week(**week_data.model_dump())
        self.db.add(new_week)
        self.db.commit()
        self.db.refresh(new_week)
        return new_week


    def update(self, week_id: int, update_data: dict) -> Optional[Week]:
        week = self.get_by_id(week_id)
        if not week:
            return None

        for key, value in update_data.items():
            setattr(week, key, value)

        self.db.commit()
        self.db.refresh(week)
        return week
    

    def delete(self, week_id: int) -> bool:
        week = self.get_by_id(week_id)
        if week:
            self.db.delete(week)
            self.db.commit()
            return True
        return False