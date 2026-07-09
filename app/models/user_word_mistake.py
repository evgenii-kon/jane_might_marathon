from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserWordMistake(Base):
    __tablename__ = "user_word_mistakes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="word_mistakes")
    word = relationship("Word", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("user_id", "word_id", name="uq_user_word_mistake"),
    )
