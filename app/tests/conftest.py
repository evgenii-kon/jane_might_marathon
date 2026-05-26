"""
Async test configuration.

Стратегия изоляции:
- Таблицы создаются ОДИН раз (sync engine) перед сессией тестов.
- Каждый тест получает ОТДЕЛЬНОЕ подключение + внешнюю транзакцию.
- AsyncSession присоединяется к этой транзакции через join_transaction_mode="create_savepoint":
  commit() внутри репозиториев выпускает SAVEPOINT вместо реального COMMIT.
- После теста вся внешняя транзакция откатывается — БД остаётся чистой.
"""

import os
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Загружаем .env.test до импорта app-конфига
load_dotenv(".env.test")

# Обязательно импортируем все модели, чтобы Base.metadata знала обо всех таблицах
from app.database import Base  # noqa: E402
import app.models  # noqa: E402  (импортирует все модели через __init__.py)

TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "postgres")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "fastapi_db_test")

ASYNC_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)
SYNC_URL = (
    f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)

# Sync-движок только для создания/удаления таблиц (без asyncio)
_sync_engine = create_engine(SYNC_URL)

# Async-движок для самих тестов (NullPool — нет пула, каждый conn независим)
async_test_engine = create_async_engine(ASYNC_URL, poolclass=NullPool, echo=False)


# ---------------------------------------------------------------------------
# Session-scoped: создаём таблицы один раз, дропаем после всех тестов
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=_sync_engine)
    yield
    Base.metadata.drop_all(bind=_sync_engine)
    _sync_engine.dispose()


# ---------------------------------------------------------------------------
# Function-scoped: каждый тест получает сессию с откатом транзакции
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """
    Открывает соединение, стартует внешнюю транзакцию,
    создаёт AsyncSession с join_transaction_mode="create_savepoint".
    После теста — rollback внешней транзакции → все изменения отменены.
    """
    async with async_test_engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(
            conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session
        await conn.rollback()
