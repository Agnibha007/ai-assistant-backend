import os
import time
import logging
import requests
from bson import ObjectId
from celery import Celery
from core.config import settings
from db.session import sync_db
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import SecretStr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

# Helper function to send commands to the bridge
def send_to_bridge(action: str, params: dict = None):
    try:
        # Internal API call to the web service to forward via WebSocket
        port = os.getenv("PORT", "10000")
        url = f"http://localhost:{port}/api/v1/tasks/bridge/execute"
        logger.info(f"Sending command to bridge via {url}")
        resp = requests.post(url, json={"action": action, "params": params or {}}, timeout=5)
        if resp.status_code != 200:
            logger.error(f"Bridge execution failed: {resp.status_code} - {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Failed to reach bridge: {e}")
        return False

@celery_app.task(name="worker.run_agent_task")
def run_agent_task(task_id: str, instruction: str) -> bool:
    logger.info(f"Worker received task: {task_id}")
    
    try:
        tasks_collection = sync_db["tasks"]
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "running"}})

        # 1. Ask LLM what to do
        # In a production app, you'd use a real API key and LangGraph
        # For now, we use a simple logic for "check emails"
        
        if "email" in instruction.lower():
            # Automation sequence for checking emails
            send_to_bridge("hotkey", {"keys": ["alt", "f2"]}) # Linux runner
            time.sleep(1)
            send_to_bridge("type", {"text": "google-chrome https://mail.google.com"})
            time.sleep(0.5)
            send_to_bridge("press", {"key": "enter"})
            result_text = "Opened browser to Gmail."
        else:
            result_text = f"I've analyzed your request: '{instruction}'. This task is currently being mapped to OS actions."

        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": "completed",
                "result": result_text
            }}
        )
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "failed", "result": str(e)}})
        return False
