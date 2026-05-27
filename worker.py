import time
import logging
from bson import ObjectId
from celery import Celery
from core.config import settings
from db.session import sync_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(name="worker.run_agent_task")
def run_agent_task(task_id: str, instruction: str) -> bool:
    logger.info(f"Worker received task: {task_id} with instruction: {instruction}")
    
    try:
        tasks_collection = sync_db["tasks"]
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return False

        logger.info(f"Updating task {task_id} status to 'running'")
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "running"}}
        )

        # Simulate processing (In future, this calls LangGraph)
        time.sleep(5)

        logger.info(f"Updating task {task_id} status to 'completed'")
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": "completed",
                "result": f"Successfully executed: {instruction}"
            }}
        )
        return True
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        if 'tasks_collection' in locals():
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"status": "failed", "result": str(e)}}
            )
        return False
