from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import Field, field_validator


class Settings(BaseSettings):
    app_name: str = "jane_might_maraphon"

    # Database settings
    DB_HOST: str = Field(..., description="Database host")
    DB_PORT: int = Field(5432, description="Database port")
    DB_USER: str = Field(..., description="Database user")
    DB_PASSWORD: str = Field(..., description="Database password")
    DB_NAME: str = Field(..., description="Database name")

    @property
    def database_url(self) -> str:
        """Формирование URL для подключения к БД (синхронная версия)"""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_async(self) -> str:
        """Формирование URL для подключения к БД (асинхронная версия)"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    

    # Redis settings
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_DB: int = Field(0, description="Redis database index")
    REDIS_PASSWORD: str = Field("", description="Redis password (if any)")

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # JWT авторизация
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    ALGORITHM: str = Field("HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(10080, description="Token TTL in minutes (default 7 days)")

    # Окружение
    DEBUG: bool = Field(False, description="Debug mode; set True only in development")

    # Static files
    static_dir: str = "static"
    images_dir: str = "static/images"

    @field_validator("images_dir")
    @classmethod
    def validate_images_dir(cls, v: str) -> str:
        """Валидация пути для изображений"""
        if not v.startswith("static/"):
            raise ValueError("images_dir must be inside static directory")
        return v


    model_config = SettingsConfigDict(
        env_file = ".env", 
        env_file_encoding = "utf-8", 
        case_sensitive = False, 
        extra = "ignore")


settings = Settings()

# Проверка загрузки настроек
if __name__ == "__main__":
    print(f"App: {settings.app_name}")
    print(f"DB URL: {settings.database_url}")
    print(f"CORS origins: {settings.cors_origins}")
