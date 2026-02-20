import asyncio
import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.creators import CreatorProfile
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _refresh_creator_profiles() -> None:
    """Refresh saved creator profiles from API."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(CreatorProfile).where(CreatorProfile.is_saved.is_(True))
        )
        creators = result.scalars().all()

        for creator in creators:
            try:
                # In production, would call TTCM API to refresh profile data
                # For now, just log
                logger.info(
                    "Refreshed creator profile %s (%s)",
                    creator.id,
                    creator.username,
                )
            except Exception:
                logger.exception("Failed to refresh creator %s", creator.id)

        await session.commit()


@celery_app.task(name="backend.workers.creator_sync.refresh_creator_profiles")
def refresh_creator_profiles() -> None:
    _run_async(_refresh_creator_profiles())
