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
    "sync-all-ad-accounts": {
        "task": "backend.workers.ad_sync.sync_all_ad_accounts",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    "sync-ad-campaigns": {
        "task": "backend.workers.ad_sync.sync_ad_campaigns",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "sync-ad-groups": {
        "task": "backend.workers.ad_sync.sync_ad_groups",
        "schedule": crontab(minute="15,45"),  # Every 30 minutes, offset
    },
    "sync-ads": {
        "task": "backend.workers.ad_sync.sync_ads",
        "schedule": crontab(minute="5,35"),  # Every 30 minutes, offset
    },
    "sync-all-videos": {
        "task": "backend.workers.content_sync.sync_all_videos",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "sync-video-metrics": {
        "task": "backend.workers.content_sync.sync_video_metrics",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    "refresh-creator-profiles": {
        "task": "backend.workers.creator_sync.refresh_creator_profiles",
        "schedule": crontab(minute=0, hour="*/12"),  # Every 12 hours
    },
    "take-daily-kpi-snapshots": {
        "task": "backend.workers.analytics_sync.take_daily_kpi_snapshots",
        "schedule": crontab(minute=0, hour=1),  # Daily at 1 AM
    },
    "run-scheduled-reports": {
        "task": "backend.workers.analytics_sync.run_scheduled_reports",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes, check for due reports
    },
    # Intelligence sync
    "sync-trends": {
        "task": "backend.workers.intelligence_sync.sync_trends",
        "schedule": crontab(minute=0, hour="*/4"),  # Every 4 hours
    },
    "sync-competitor-content": {
        "task": "backend.workers.intelligence_sync.sync_competitor_content",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    # LIVE sync
    "cleanup-stale-live-sessions": {
        "task": "backend.workers.live_sync.cleanup_stale_sessions",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Messaging sync
    "sync-conversations": {
        "task": "backend.workers.messaging_sync.sync_conversations",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "sync-mentions": {
        "task": "backend.workers.messaging_sync.sync_mentions",
        "schedule": crontab(minute=0, hour="*/2"),  # Every 2 hours
    },
}
