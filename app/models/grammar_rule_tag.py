from sqlalchemy import Table, Column, Integer, ForeignKey
from ..database import Base

grammar_rule_tags = Table(
    "grammar_rule_tags",
    Base.metadata,
    Column("rule_id", Integer, ForeignKey("grammar_rules.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("grammar_tags.id", ondelete="CASCADE"), primary_key=True),
)
