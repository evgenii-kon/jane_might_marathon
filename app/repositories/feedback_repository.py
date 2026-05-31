from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.feedback import FeedBack
from app.schemas.feedback import FeedbackCreate
from typing import Optional, List


class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, data: FeedbackCreate) -> FeedBack:
        feedback = FeedBack(user_id=user_id, text=data.text)
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_by_user(self, user_id: int) -> List[FeedBack]:
        result = await self.db.execute(
            select(FeedBack)
            .where(FeedBack.user_id == user_id)
            .order_by(FeedBack.created_at.desc())
        )
        return result.scalars().all()

    async def get_all(self) -> List[FeedBack]:
        result = await self.db.execute(select(FeedBack))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Optional[FeedBack]:
        result = await self.db.execute(
            select(FeedBack).where(FeedBack.id == id)
        )
        return result.scalar_one_or_none()

    async def delete(self, feedback_id: int) -> bool:
        feedback = await self.get_by_id(feedback_id)
        if feedback:
            await self.db.delete(feedback)
            await self.db.commit()
            return True
        return False