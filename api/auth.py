from typing import Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.security import create_access_token, get_password_hash, verify_password
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from schemas.user import UserCreate, UserResponse

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)) -> Any:
    user = await db["users"].find_one({"email": user_in.email})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    user_data = {
        "email": user_in.email,
        "hashed_password": get_password_hash(user_in.password),
        "is_active": True,
        "created_at": None, # Will be set by pydantic or mongodb
    }
    
    result = await db["users"].insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data


@router.post("/login", response_model=Token)
async def login(
    db: AsyncIOMotorDatabase = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, str(user["hashed_password"])):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {
        "access_token": create_access_token(str(user["_id"])),
        "token_type": "bearer",
    }
