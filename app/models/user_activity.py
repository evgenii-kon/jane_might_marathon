from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    activity_count = Column(Integer, default=1, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_activity_date"),)

    user = relationship("User", back_populates="activities")
