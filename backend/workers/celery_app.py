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
# Minutes are staggered to avoid thundering-herd (all tasks firing at minute=0).
celery_app.conf.beat_schedule = {
    "refresh-developer-tokens": {
        "task": "backend.workers.token_refresh.refresh_developer_tokens",
        "schedule": crontab(minute=3, hour="*/12"),  # Every 12h, offset :03
    },
    "refresh-shop-tokens": {
        "task": "backend.workers.token_refresh.refresh_shop_tokens",
        "schedule": crontab(minute=7, hour=0),  # Daily at 00:07
    },
    "check-marketing-tokens": {
        "task": "backend.workers.token_refresh.check_marketing_tokens",
        "schedule": crontab(minute=12, hour=6),  # Daily at 06:12
    },
    "sync-shop-orders": {
        "task": "backend.workers.data_sync.sync_shop_orders",
        "schedule": crontab(minute="2,17,32,47"),  # ~Every 15 min, offset :02
    },
    "sync-shop-products": {
        "task": "backend.workers.data_sync.sync_shop_products",
        "schedule": crontab(minute="8,38"),  # ~Every 30 min, offset :08
    },
    "sync-all-ad-accounts": {
        "task": "backend.workers.ad_sync.sync_all_ad_accounts",
        "schedule": crontab(minute=18, hour="*/6"),  # Every 6h, offset :18
    },
    "sync-ad-campaigns": {
        "task": "backend.workers.ad_sync.sync_ad_campaigns",
        "schedule": crontab(minute="10,40"),  # ~Every 30 min, offset :10
    },
    "sync-ad-groups": {
        "task": "backend.workers.ad_sync.sync_ad_groups",
        "schedule": crontab(minute="15,45"),  # Every 30 min, offset :15
    },
    "sync-ads": {
        "task": "backend.workers.ad_sync.sync_ads",
        "schedule": crontab(minute="5,35"),  # Every 30 min, offset :05
    },
    "sync-all-videos": {
        "task": "backend.workers.content_sync.sync_all_videos",
        "schedule": crontab(minute="22,52"),  # ~Every 30 min, offset :22
    },
    "sync-video-metrics": {
        "task": "backend.workers.content_sync.sync_video_metrics",
        "schedule": crontab(minute=27, hour="*/6"),  # Every 6h, offset :27
    },
    "refresh-creator-profiles": {
        "task": "backend.workers.creator_sync.refresh_creator_profiles",
        "schedule": crontab(minute=33, hour="*/12"),  # Every 12h, offset :33
    },
    "take-daily-kpi-snapshots": {
        "task": "backend.workers.analytics_sync.take_daily_kpi_snapshots",
        "schedule": crontab(minute=5, hour=1),  # Daily at 01:05
    },
    "run-scheduled-reports": {
        "task": "backend.workers.analytics_sync.run_scheduled_reports",
        "schedule": crontab(minute="13,43"),  # ~Every 30 min, offset :13
    },
    # Intelligence sync
    "sync-trends": {
        "task": "backend.workers.intelligence_sync.sync_trends",
        "schedule": crontab(minute=42, hour="*/4"),  # Every 4h, offset :42
    },
    "sync-competitor-content": {
        "task": "backend.workers.intelligence_sync.sync_competitor_content",
        "schedule": crontab(minute=48, hour="*/6"),  # Every 6h, offset :48
    },
    # LIVE sync
    "cleanup-stale-live-sessions": {
        "task": "backend.workers.live_sync.cleanup_stale_sessions",
        "schedule": crontab(minute=55),  # Every hour at :55
    },
    # Messaging sync
    "sync-conversations": {
        "task": "backend.workers.messaging_sync.sync_conversations",
        "schedule": crontab(minute="20,50"),  # ~Every 30 min, offset :20
    },
    "sync-mentions": {
        "task": "backend.workers.messaging_sync.sync_mentions",
        "schedule": crontab(minute=37, hour="*/2"),  # Every 2h, offset :37
    },
}


@celery_app.task(name="backend.workers.celery_app.worker_health_check")
def worker_health_check() -> dict[str, str]:
    """Return a simple health status. Ping this from the API health endpoint
    to verify that at least one Celery worker is alive and processing tasks.

    Usage from FastAPI::

        result = worker_health_check.delay()
        status = result.get(timeout=5)  # {"status": "healthy"}
    """
    return {"status": "healthy"}
