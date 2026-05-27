import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Desktop Assistant Core API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "assistant_db")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # CORS Configuration
    # We use a string and split it manually to avoid Pydantic's automatic JSON parsing of lists
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,*"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "JSON")  # JSON or TEXT


settings = Settings()
