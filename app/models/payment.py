from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tinkoff_payment_id = Column(String(50), unique=True, nullable=True)
    order_id = Column(String(100), unique=True, nullable=False)
    amount_kopecks = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="NEW")
    payment_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    subscription = relationship("Subscription", back_populates="payments")
    user = relationship("User")
