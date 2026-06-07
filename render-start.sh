#!/bin/bash

# 1. Run database migrations
alembic upgrade head

# 2. Start Celery worker in the background
# We limit concurrency to 2 to stay within Render's free 512MB RAM limit
celery -A app.core.celery worker --loglevel=info --concurrency=2 &

# 3. Start FastAPI in the foreground
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}