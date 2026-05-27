import time
from bson import ObjectId
from celery import Celery
from core.config import settings
from db.session import sync_db

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.task_routes = {"worker.run_agent_task": "main-queue"}


@celery_app.task(name="worker.run_agent_task")
def run_agent_task(task_id: str, instruction: str) -> bool:
    # This will be replaced by LangGraph execution
    # For now, it's a stub

    tasks_collection = sync_db["tasks"]
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    
    if task:
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "running"}}
        )

        # Simulate processing
        time.sleep(2)

        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": "completed",
                "result": f"Successfully simulated execution of: {instruction}"
            }}
        )
    return True
