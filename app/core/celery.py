from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "my background app",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=300,
    task_time_limit=330,
    worker_max_tasks_per_child=10,
    worker_concurrency=2,  # Dont know about this
)
