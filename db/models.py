from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class MongoBaseModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True

class User(MongoBaseModel):
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(MongoBaseModel):
    description: str
    status: str = "pending"
    result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
