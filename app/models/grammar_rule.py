from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from .grammar_rule_tag import grammar_rule_tags


class GrammarRule(Base):
    __tablename__ = "grammar_rules"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    hsk_level = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tags = relationship("GrammarTag", secondary=grammar_rule_tags, back_populates="rules")
