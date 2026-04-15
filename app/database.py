from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from .config import settings

engine = create_engine(settings.database_url)

if not database_exists(engine.url):
    create_database(engine.url)

new_session = sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = new_session()
    try:
        yield db
    finally:
        db.close()
        