from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_kopecks = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False, default=90)
    features = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    badge = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    subscriptions = relationship("Subscription", back_populates="plan", lazy="selectin")

    @property
    def price_display(self) -> str:
        rub = self.price_kopecks // 100
        kop = self.price_kopecks % 100
        if kop:
            return f"{rub},{kop:02d} ₽"
        return f"{rub} ₽"
