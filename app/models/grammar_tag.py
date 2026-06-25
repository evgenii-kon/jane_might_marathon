from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from .grammar_rule_tag import grammar_rule_tags


class GrammarTag(Base):
    __tablename__ = "grammar_tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    rules = relationship("GrammarRule", secondary=grammar_rule_tags, back_populates="tags")
