from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserWeekProgress(Base):
    __tablename__ = 'user_week_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    week_id = Column(Integer, ForeignKey("weeks.id"))
    
    opens_at = Column(DateTime(timezone=True), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True) 

    user = relationship("User", back_populates="week_progress")
    week = relationship("Week", back_populates="user_progress")