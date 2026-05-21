import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Импортируем общую Base из приложения
from app.database import Base
# Импортируем все модели, чтобы они попали в Base.metadata

load_dotenv('.env.test')

TEST_DB_USER = os.getenv('TEST_DB_USER')
TEST_DB_PASSWORD = os.getenv('TEST_DB_PASSWORD')
TEST_DB_HOST = os.getenv('TEST_DB_HOST')
TEST_DB_PORT = os.getenv('TEST_DB_PORT')
TEST_DB_NAME = os.getenv('TEST_DB_NAME')


TEST_DATABASE_URL = f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Создаёт таблицы в тестовой БД один раз перед всеми тестами"""
    Base.metadata.create_all(bind=engine)
    yield
    # Это безопасно, так как мы уверены, что это тестовая БД
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Фикстура для тестовой сессии с откатом транзакции"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:  
            transaction.rollback()
        connection.close()