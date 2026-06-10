#!/bin/bash

# 1. Run database migrations
alembic upgrade head

# 2. Start Celery worker in the background
# We limit concurrency to 1 to stay within Render's free 512MB RAM limit
celery -A app.core.celery worker --loglevel=info --concurrency=1 &

# 3. Start FastAPI in the foreground
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000