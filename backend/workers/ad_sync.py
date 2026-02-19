import asyncio
import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_group_service import AdGroupService
from backend.modules.advertising.services.ad_service import AdService
from backend.modules.advertising.services.campaign_service import CampaignService
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_all_ad_accounts() -> None:
    """Discover advertiser IDs from Marketing ConnectedAccounts."""
    from backend.modules.advertising.services.ad_account_service import (
        AdAccountService,
    )
    from backend.db.models.organization import Workspace

    async with async_session_factory() as session:
        result = await session.execute(select(Workspace))
        workspaces = result.scalars().all()

        for workspace in workspaces:
            try:
                service = AdAccountService(session)
                synced = await service.sync_ad_accounts_from_connected(
                    workspace.id
                )
                await session.commit()
                logger.info(
                    "Synced %d ad accounts for workspace %s",
                    len(synced),
                    workspace.id,
                )
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync ad accounts for workspace %s",
                    workspace.id,
                )


async def _sync_ad_campaigns() -> None:
    """Paginate /v1.3/campaign/get/ for all active ad accounts."""
    async with async_session_factory() as session:
        result = await session.execute(select(AdAccount))
        ad_accounts = result.scalars().all()

        for ad_account in ad_accounts:
            try:
                service = CampaignService(session)
                synced = await service.sync_campaigns(ad_account)
                await session.commit()
                logger.info(
                    "Synced %d campaigns for ad account %s",
                    synced,
                    ad_account.advertiser_id,
                )
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync campaigns for ad account %s",
                    ad_account.advertiser_id,
                )


async def _sync_ad_groups() -> None:
    """Paginate /v1.3/adgroup/get/ for all active ad accounts."""
    async with async_session_factory() as session:
        result = await session.execute(select(AdAccount))
        ad_accounts = result.scalars().all()

        for ad_account in ad_accounts:
            try:
                service = AdGroupService(session)
                synced = await service.sync_ad_groups(ad_account)
                await session.commit()
                logger.info(
                    "Synced %d ad groups for ad account %s",
                    synced,
                    ad_account.advertiser_id,
                )
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync ad groups for ad account %s",
                    ad_account.advertiser_id,
                )


async def _sync_ads() -> None:
    """Paginate /v1.3/ad/get/ for all active ad accounts."""
    async with async_session_factory() as session:
        result = await session.execute(select(AdAccount))
        ad_accounts = result.scalars().all()

        for ad_account in ad_accounts:
            try:
                service = AdService(session)
                synced = await service.sync_ads(ad_account)
                await session.commit()
                logger.info(
                    "Synced %d ads for ad account %s",
                    synced,
                    ad_account.advertiser_id,
                )
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync ads for ad account %s",
                    ad_account.advertiser_id,
                )


async def _sync_single_ad_account(ad_account_id: str) -> None:
    """Full sync (campaigns + ad groups + ads) for one ad account."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(AdAccount).where(AdAccount.id == ad_account_id)
        )
        ad_account = result.scalar_one_or_none()
        if not ad_account:
            logger.warning("Ad account %s not found", ad_account_id)
            return

        try:
            campaign_service = CampaignService(session)
            campaigns_synced = await campaign_service.sync_campaigns(ad_account)

            adgroup_service = AdGroupService(session)
            adgroups_synced = await adgroup_service.sync_ad_groups(ad_account)

            ad_service = AdService(session)
            ads_synced = await ad_service.sync_ads(ad_account)

            await session.commit()
            logger.info(
                "Full sync for ad account %s: %d campaigns, %d ad groups, %d ads",
                ad_account.advertiser_id,
                campaigns_synced,
                adgroups_synced,
                ads_synced,
            )
        except Exception:
            await session.rollback()
            logger.exception(
                "Failed full sync for ad account %s",
                ad_account.advertiser_id,
            )


@celery_app.task(name="backend.workers.ad_sync.sync_all_ad_accounts")
def sync_all_ad_accounts() -> None:
    _run_async(_sync_all_ad_accounts())


@celery_app.task(name="backend.workers.ad_sync.sync_ad_campaigns")
def sync_ad_campaigns() -> None:
    _run_async(_sync_ad_campaigns())


@celery_app.task(name="backend.workers.ad_sync.sync_ad_groups")
def sync_ad_groups() -> None:
    _run_async(_sync_ad_groups())


@celery_app.task(name="backend.workers.ad_sync.sync_ads")
def sync_ads() -> None:
    _run_async(_sync_ads())


@celery_app.task(name="backend.workers.ad_sync.sync_single_ad_account")
def sync_single_ad_account(ad_account_id: str) -> None:
    _run_async(_sync_single_ad_account(ad_account_id))
