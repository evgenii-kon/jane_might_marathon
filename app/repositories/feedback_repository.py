from sqlalchemy.orm import Session
from app.models.feedback import FeedBack
from app.schemas.feedback import FeedbackCreate
from typing import List


class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db


    def create(self, user_id: int, data: FeedbackCreate) -> FeedBack:
        feedback = FeedBack(user_id=user_id, text=data.text)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback


    def get_by_user(self, user_id: int) -> list[FeedBack]:
        return self.db.query(FeedBack).filter(FeedBack.user_id == user_id).order_by(FeedBack.created_at.desc()).all()
    

    def get_all(self) -> List[FeedBack]:
        return self.db.query(FeedBack).all()
    

    def get_by_id(self, id: int) -> FeedBack:
        return self.db.query(FeedBack).filter(FeedBack.id == id).first()
    

    def delete(self, feedback_id: int) -> bool:
        feedback = self.get_by_id(feedback_id)
        if feedback:
            self.db.delete(feedback)
            self.db.commit()
            return True
        return False