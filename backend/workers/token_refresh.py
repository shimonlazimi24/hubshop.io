import asyncio
import logging

import httpx
from sqlalchemy import select

from backend.config import settings
from backend.db.engine import async_session_factory
from backend.db.models.platform import AccountStatus, ConnectedAccount, Platform, TokenVault
from backend.utils.crypto import decrypt_token, encrypt_token
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    """Run an async function from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _refresh_developer_token(account_id, refresh_token: str) -> dict | None:  # type: ignore[no-untyped-def]
    """Exchange refresh token for new Developer API tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": settings.tiktok_developer_client_key,
                "client_secret": settings.tiktok_developer_client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            if "access_token" in data:
                return data
    logger.error("Developer token refresh failed for account %s", account_id)
    return None


async def _refresh_shop_token(account_id, refresh_token: str) -> dict | None:  # type: ignore[no-untyped-def]
    """Exchange refresh token for new Shop API tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://auth.tiktok-shops.com/api/v2/token/refresh",
            params={
                "app_key": settings.tiktok_shop_app_key,
                "app_secret": settings.tiktok_shop_app_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data")
    logger.error("Shop token refresh failed for account %s", account_id)
    return None


async def _do_refresh_developer_tokens() -> None:
    """Refresh all Developer platform tokens."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ConnectedAccount)
            .where(ConnectedAccount.platform == Platform.DEVELOPER)
            .where(ConnectedAccount.status == AccountStatus.ACTIVE)
        )
        accounts = result.scalars().all()

        for account in accounts:
            vault_result = await session.execute(
                select(TokenVault).where(TokenVault.connected_account_id == account.id)
            )
            vault = vault_result.scalar_one_or_none()
            if not vault or not vault.encrypted_refresh_token:
                continue

            refresh_token = decrypt_token(vault.encrypted_refresh_token)
            new_tokens = await _refresh_developer_token(account.id, refresh_token)

            if new_tokens:
                vault.encrypted_access_token = encrypt_token(new_tokens["access_token"])
                if new_tokens.get("refresh_token"):
                    vault.encrypted_refresh_token = encrypt_token(new_tokens["refresh_token"])
                vault.access_token_expires_at = str(new_tokens.get("expires_in", ""))
                logger.info("Refreshed Developer token for account %s", account.id)
            else:
                account.status = AccountStatus.ERROR
                logger.warning("Marked Developer account %s as error", account.id)

        await session.commit()


async def _do_refresh_shop_tokens() -> None:
    """Refresh all Shop platform tokens."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ConnectedAccount)
            .where(ConnectedAccount.platform == Platform.SHOP)
            .where(ConnectedAccount.status == AccountStatus.ACTIVE)
        )
        accounts = result.scalars().all()

        for account in accounts:
            vault_result = await session.execute(
                select(TokenVault).where(TokenVault.connected_account_id == account.id)
            )
            vault = vault_result.scalar_one_or_none()
            if not vault or not vault.encrypted_refresh_token:
                continue

            refresh_token = decrypt_token(vault.encrypted_refresh_token)
            new_tokens = await _do_refresh_shop_token_single(account, vault, refresh_token, session)

        await session.commit()


async def _do_refresh_shop_token_single(account, vault, refresh_token, session) -> None:  # type: ignore[no-untyped-def]
    new_tokens = await _refresh_shop_token(account.id, refresh_token)
    if new_tokens:
        vault.encrypted_access_token = encrypt_token(new_tokens["access_token"])
        if new_tokens.get("refresh_token"):
            vault.encrypted_refresh_token = encrypt_token(new_tokens["refresh_token"])
        vault.access_token_expires_at = str(new_tokens.get("access_token_expire_in", ""))
        logger.info("Refreshed Shop token for account %s", account.id)
    else:
        account.status = AccountStatus.ERROR
        logger.warning("Marked Shop account %s as error", account.id)


async def _do_check_marketing_tokens() -> None:
    """Verify Marketing tokens are still valid."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ConnectedAccount)
            .where(ConnectedAccount.platform == Platform.MARKETING)
            .where(ConnectedAccount.status == AccountStatus.ACTIVE)
        )
        accounts = result.scalars().all()

        for account in accounts:
            vault_result = await session.execute(
                select(TokenVault).where(TokenVault.connected_account_id == account.id)
            )
            vault = vault_result.scalar_one_or_none()
            if not vault:
                continue

            access_token = decrypt_token(vault.encrypted_access_token)
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://business-api.tiktok.com/open_api/v1.3/user/info/",
                    headers={"Access-Token": access_token},
                )
                if resp.status_code != 200 or resp.json().get("code") != 0:
                    account.status = AccountStatus.ERROR
                    logger.warning("Marketing token invalid for account %s", account.id)

        await session.commit()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="backend.workers.token_refresh.refresh_developer_tokens",
)
def refresh_developer_tokens(self) -> None:  # type: ignore[no-untyped-def]
    try:
        _run_async(_do_refresh_developer_tokens())
    except Exception as exc:
        logger.exception("Developer token refresh task failed")
        self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="backend.workers.token_refresh.refresh_shop_tokens",
)
def refresh_shop_tokens(self) -> None:  # type: ignore[no-untyped-def]
    try:
        _run_async(_do_refresh_shop_tokens())
    except Exception as exc:
        logger.exception("Shop token refresh task failed")
        self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="backend.workers.token_refresh.check_marketing_tokens",
)
def check_marketing_tokens(self) -> None:  # type: ignore[no-untyped-def]
    try:
        _run_async(_do_check_marketing_tokens())
    except Exception as exc:
        logger.exception("Marketing token check task failed")
        self.retry(exc=exc)
