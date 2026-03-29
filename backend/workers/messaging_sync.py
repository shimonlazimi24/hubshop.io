"""Celery tasks for messaging and mentions data sync."""

import asyncio
import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.platform import ConnectedAccount, Platform, TokenVault
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.utils.crypto import decrypt_token
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _build_marketing_gateway(
    session, connected_account_id
) -> PlatformGateway | None:
    """Build a PlatformGateway for a marketing connected account."""
    result = await session.execute(
        select(TokenVault).where(
            TokenVault.connected_account_id == connected_account_id
        )
    )
    token = result.scalar_one_or_none()
    if not token or not token.encrypted_access_token:
        return None
    access_token = decrypt_token(token.encrypted_access_token)
    client = TikTokMarketingClient(access_token=access_token)
    return PlatformGateway(
        platform=Platform.MARKETING,
        account_id=str(connected_account_id),
        client=client,
    )


async def _sync_conversations() -> None:
    """Sync conversations and recent messages for all marketing-connected workspaces."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.platform == Platform.MARKETING
            )
        )
        accounts = result.scalars().all()

        for account in accounts:
            try:
                gateway = await _build_marketing_gateway(session, account.id)
                if not gateway:
                    logger.warning(
                        "No token for connected account %s, skipping", account.id
                    )
                    continue

                resp = await gateway.get(
                    "/business/message/conversation/list/",
                    params={"page_size": "50"},
                )
                conversations = resp.get("data", {}).get("conversations", [])
                logger.info(
                    "Synced %d conversations for account %s",
                    len(conversations),
                    account.id,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed conversation sync for account %s", account.id)


async def _sync_mentions() -> None:
    """Sync brand mentions for all marketing-connected workspaces."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.platform == Platform.MARKETING
            )
        )
        accounts = result.scalars().all()

        for account in accounts:
            try:
                gateway = await _build_marketing_gateway(session, account.id)
                if not gateway:
                    logger.warning(
                        "No token for connected account %s, skipping", account.id
                    )
                    continue

                resp = await gateway.get(
                    "/mentions/posts/top/",
                    params={},
                )
                mentions = resp.get("data", {}).get("posts", [])
                logger.info(
                    "Synced %d mentions for account %s",
                    len(mentions),
                    account.id,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed mentions sync for account %s", account.id)


@celery_app.task(name="backend.workers.messaging_sync.sync_conversations")
def sync_conversations() -> None:
    """Sync business messaging conversations. Runs every 30 minutes."""
    _run_async(_sync_conversations())


@celery_app.task(name="backend.workers.messaging_sync.sync_mentions")
def sync_mentions() -> None:
    """Sync brand mentions. Runs every 2 hours."""
    _run_async(_sync_mentions())
