from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import sqlalchemy as sa
from .config import settings

engine = create_async_engine(
    settings.database_url_async,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    """Проверка подключения к БД при старте. Схема управляется через Alembic."""
    async with engine.connect() as conn:
        await conn.execute(sa.text("SELECT 1"))

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session