from collections.abc import Generator
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from core.config import settings

# Async client for FastAPI
async_client = AsyncIOMotorClient(settings.MONGODB_URL)
async_db = async_client[settings.MONGODB_DB_NAME]

# Sync client for Celery
sync_client = MongoClient(settings.MONGODB_URL)
sync_db = sync_client[settings.MONGODB_DB_NAME]

def get_db():
    return async_db
