"""Celery tasks for intelligence module data sync."""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from backend.config import settings
from backend.db.engine import async_session_factory
from backend.db.models.organization import Workspace
from backend.modules.intelligence.services.competitor_service import (
    CompetitorService,
)
from backend.modules.intelligence.services.trend_service import TrendService
from backend.tiktok.research.client import TikTokResearchClient
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_trends() -> None:
    """Sync trending hashtags, sounds, and products for all workspaces."""
    if not settings.tiktok_research_client_key:
        logger.warning("Research API credentials not configured, skipping trend sync")
        return

    research_client = TikTokResearchClient(
        client_key=settings.tiktok_research_client_key,
        client_secret=settings.tiktok_research_client_secret,
    )

    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Workspace))
            workspaces = result.scalars().all()

            for workspace in workspaces:
                try:
                    service = TrendService(session)
                    await service.sync_trends(workspace.id, research_client)
                    await session.commit()
                    logger.info("Synced trends for workspace %s", workspace.id)
                except Exception:
                    await session.rollback()
                    logger.exception(
                        "Failed trend sync for workspace %s", workspace.id
                    )
    finally:
        await research_client.close()


async def _sync_competitor_content() -> None:
    """Sync latest content for all tracked competitors."""
    if not settings.tiktok_research_client_key:
        logger.warning(
            "Research API credentials not configured, skipping competitor sync"
        )
        return

    research_client = TikTokResearchClient(
        client_key=settings.tiktok_research_client_key,
        client_secret=settings.tiktok_research_client_secret,
    )

    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Workspace))
            workspaces = result.scalars().all()

            for workspace in workspaces:
                try:
                    service = CompetitorService(session)
                    await service.sync_all_competitors(workspace.id, research_client)
                    await session.commit()
                    logger.info(
                        "Synced competitor content for workspace %s", workspace.id
                    )
                except Exception:
                    await session.rollback()
                    logger.exception(
                        "Failed competitor sync for workspace %s", workspace.id
                    )
    finally:
        await research_client.close()


@celery_app.task(name="backend.workers.intelligence_sync.sync_trends")
def sync_trends() -> None:
    """Sync trending content from Research API. Runs every 4 hours."""
    _run_async(_sync_trends())


@celery_app.task(name="backend.workers.intelligence_sync.sync_competitor_content")
def sync_competitor_content() -> None:
    """Sync competitor content from Research API. Runs every 6 hours."""
    _run_async(_sync_competitor_content())
