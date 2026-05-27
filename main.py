from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from api.auth import router as auth_router
from core.config import settings
from db.models import Base
from db.session import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware


# Create tables for now, in production use Alembic
def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # In a real app, you might want to handle this differently
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
    yield


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", lifespan=lifespan)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])


@app.get("/health")
def health_check() -> Any:
    return {"status": "ok", "service": "core-api"}
