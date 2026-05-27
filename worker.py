import time

from celery import Celery
from core.config import settings
from db.models import Task
from db.session import SessionLocal

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.task_routes = {"worker.run_agent_task": "main-queue"}


@celery_app.task(name="worker.run_agent_task")
def run_agent_task(task_id: int, instruction: str) -> bool:
    # This will be replaced by LangGraph execution
    # For now, it's a stub

    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "running"
        db.commit()

        # Simulate processing
        time.sleep(2)

        task.status = "completed"
        task.result = f"Successfully simulated execution of: {instruction}"
        db.commit()
    db.close()
    return True
