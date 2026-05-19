from sqlalchemy.orm import Session
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse


class FeedbackService:
    def __init__(self, db: Session):
        self.repo = FeedbackRepository(db)


    def create_feedback(self, user_id: int, data: FeedbackCreate) -> FeedbackResponse:
        feedback = self.repo.create(user_id, data)
        return FeedbackResponse.model_validate(feedback)


    def get_user_feedback(self, user_id: int) -> list[FeedbackResponse]:
        feedbacks = self.repo.get_by_user(user_id)
        return [FeedbackResponse.model_validate(f) for f in feedbacks]
    

    def get_by_id(self, id: int) -> FeedbackResponse:
        feedback = self.repo.get_by_id(id)
        return FeedbackResponse.model_validate(feedback)


    def get_all(self):
        feedbacks = self.repo.get_all()
        return [FeedbackResponse.model_validate(f) for f in feedbacks]
    

    def delete(self, feedback_id: int) -> bool:
        return self.repo.delete(feedback_id)