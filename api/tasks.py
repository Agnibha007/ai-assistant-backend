from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase
from db.session import get_db
from pydantic import BaseModel
from worker import run_agent_task
from bson import ObjectId

router = APIRouter()

# Global dictionary to track connected host-bridge clients
connected_bridges: dict[str, WebSocket] = {}

class TaskCreate(BaseModel):
    description: str

class TaskResponse(BaseModel):
    id: str
    description: str
    status: str
    result: str | None = None

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Any:
    task_data = {
        "description": task_in.description,
        "status": "pending",
        "result": None,
        "created_at": None
    }
    result = await db["tasks"].insert_one(task_data)
    task_id = str(result.inserted_id)
    
    # Trigger Celery worker
    run_agent_task.delay(task_id, task_in.description)
    
    task_data["id"] = task_id
    return task_data

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Any:
    task = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["id"] = str(task["_id"])
    return task

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Any:
    tasks = await db["tasks"].find().sort("created_at", -1).to_list(100)
    for task in tasks:
        task["id"] = str(task["_id"])
    return tasks

# WebSocket for Host Bridge to connect
@router.websocket("/ws/bridge")
async def bridge_websocket(websocket: WebSocket, client_id: str = "default"):
    await websocket.accept()
    connected_bridges[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        if client_id in connected_bridges:
            del connected_bridges[client_id]

# Internal endpoint for Worker to send commands to Bridge
@router.post("/bridge/execute")
async def execute_on_bridge(command: dict, client_id: str = "default"):
    if client_id not in connected_bridges:
        raise HTTPException(status_code=404, detail="Bridge not connected")
    
    ws = connected_bridges[client_id]
    await ws.send_json(command)
    return {"status": "sent"}
