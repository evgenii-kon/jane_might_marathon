from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base


class UserNovelProgress(Base):
    """Отмечает, что пользователь уже видел новеллу перед конкретным уроком —
    чтобы не показывать её автоматически повторно при следующем заходе в урок."""

    __tablename__ = "user_novel_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_novel_progress"),
    )
