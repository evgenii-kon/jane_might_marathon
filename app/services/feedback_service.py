from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException, status
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse


class FeedbackService:
    def __init__(self, db: AsyncSession):
        self.repo = FeedbackRepository(db)

    async def create_feedback(self, user_id: int, data: FeedbackCreate) -> FeedbackResponse:
        feedback = await self.repo.create(user_id, data)
        return FeedbackResponse.model_validate(feedback)

    async def get_user_feedback(self, user_id: int) -> List[FeedbackResponse]:
        feedbacks = await self.repo.get_by_user(user_id)
        return [FeedbackResponse.model_validate(f) for f in feedbacks]

    async def get_by_id(self, feedback_id: int) -> FeedbackResponse:
        feedback = await self.repo.get_by_id(feedback_id)
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback with id={feedback_id} not found"
            )
        return FeedbackResponse.model_validate(feedback)

    async def get_all(self) -> List[FeedbackResponse]:
        feedbacks = await self.repo.get_all()
        return [FeedbackResponse.model_validate(f) for f in feedbacks]

    async def delete(self, feedback_id: int) -> bool:
        return await self.repo.delete(feedback_id)