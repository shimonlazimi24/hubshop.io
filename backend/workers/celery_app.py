from celery import Celery
from celery.schedules import crontab

from backend.config import settings

celery_app = Celery(
    "frodo",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks in workers module
celery_app.autodiscover_tasks(["backend.workers"])

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "refresh-developer-tokens": {
        "task": "backend.workers.token_refresh.refresh_developer_tokens",
        "schedule": crontab(minute=0, hour="*/12"),  # Every 12 hours
    },
    "refresh-shop-tokens": {
        "task": "backend.workers.token_refresh.refresh_shop_tokens",
        "schedule": crontab(minute=0, hour=0),  # Daily at midnight
    },
    "check-marketing-tokens": {
        "task": "backend.workers.token_refresh.check_marketing_tokens",
        "schedule": crontab(minute=0, hour=6),  # Daily at 6 AM
    },
    "sync-shop-orders": {
        "task": "backend.workers.data_sync.sync_shop_orders",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "sync-shop-products": {
        "task": "backend.workers.data_sync.sync_shop_products",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
}
