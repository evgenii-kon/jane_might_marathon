from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserIdiomProgress(Base):
    __tablename__ = "user_idiom_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    idiom_id = Column(Integer, ForeignKey("idioms.id"), nullable=False, index=True)
    # "not_known" | "learning" | "known"
    status = Column(String(20), nullable=False, default="not_known")
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="idiom_progress")
    idiom = relationship("Idiom", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "idiom_id", name="uq_user_idiom_progress"),
    )
