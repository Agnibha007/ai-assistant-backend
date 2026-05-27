#!/bin/bash

echo "Starting Celery worker..."
# Start Celery worker in the background
# We use the default queue and increase log level
celery -A worker.celery_app worker --loglevel=info --concurrency=1 &

echo "Starting FastAPI API..."
# Start FastAPI API in the foreground
uvicorn main:app --host 0.0.0.0 --port $PORT
