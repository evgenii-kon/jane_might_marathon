from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserReadingProgress(Base):
    __tablename__ = "user_reading_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text_id = Column(Integer, ForeignKey("reading_texts.id", ondelete="CASCADE"), nullable=False, index=True)
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reading_progress")
    text = relationship("ReadingText", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "text_id", name="uq_user_reading_progress"),
    )
