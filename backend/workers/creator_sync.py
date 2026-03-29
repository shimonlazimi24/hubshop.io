import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.creators import CreatorProfile
from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.developer.client import TikTokDeveloperClient
from backend.tiktok.gateway import PlatformGateway
from backend.utils.crypto import decrypt_token
from backend.workers.async_utils import async_task
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _build_developer_gateway(
    session,  # type: ignore[no-untyped-def]
    account: ConnectedAccount,
) -> PlatformGateway:
    """Build a PlatformGateway for a Developer connected account."""
    result = await session.execute(
        select(TokenVault).where(TokenVault.connected_account_id == account.id)
    )
    vault = result.scalar_one_or_none()
    if not vault:
        raise ValueError(f"No token vault for account {account.id}")

    access_token = decrypt_token(vault.encrypted_access_token)
    client = TikTokDeveloperClient(access_token=access_token)
    return PlatformGateway(
        platform=Platform.DEVELOPER,
        account_id=str(account.id),
        client=client,
    )


async def _refresh_creator_profiles() -> None:
    """Refresh saved creator profiles by fetching latest data from Developer API.

    For each saved creator, queries the Developer API /user/info/ endpoint
    to get updated follower counts, bio, avatar, etc.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(CreatorProfile).where(CreatorProfile.is_saved.is_(True))
        )
        creators = result.scalars().all()
        if not creators:
            return

        # Group creators by workspace to reuse gateway connections
        workspace_creators: dict[str, list[CreatorProfile]] = {}
        for creator in creators:
            ws_id = str(creator.workspace_id)
            workspace_creators.setdefault(ws_id, []).append(creator)

        for ws_id, ws_creators in workspace_creators.items():
            # Find an active Developer account for this workspace
            acct_result = await session.execute(
                select(ConnectedAccount).where(
                    ConnectedAccount.workspace_id == ws_id,
                    ConnectedAccount.platform == Platform.DEVELOPER,
                    ConnectedAccount.status == AccountStatus.ACTIVE,
                )
            )
            account = acct_result.scalars().first()
            if not account:
                logger.warning(
                    "No active Developer account for workspace %s, skipping %d creators",
                    ws_id,
                    len(ws_creators),
                )
                continue

            try:
                gateway = await _build_developer_gateway(session, account)
            except Exception:
                logger.exception("Failed to build gateway for workspace %s", ws_id)
                continue

            for creator in ws_creators:
                try:
                    resp = await gateway.post(
                        "/user/info/",
                        json_body={},
                        params={
                            "fields": "display_name,avatar_url,bio_description,"
                            "follower_count,following_count,likes_count,video_count"
                        },
                    )
                    data = resp.get("data", {}).get("user", {})
                    if data:
                        creator.display_name = data.get(
                            "display_name", creator.display_name
                        )
                        creator.avatar_url = data.get("avatar_url", creator.avatar_url)
                        creator.bio = data.get("bio_description", creator.bio)
                        creator.follower_count = data.get(
                            "follower_count", creator.follower_count
                        )
                        creator.following_count = data.get(
                            "following_count", creator.following_count
                        )
                        creator.likes_count = data.get(
                            "likes_count", creator.likes_count
                        )
                        creator.video_count = data.get(
                            "video_count", creator.video_count
                        )
                        creator.detail_json = data

                    logger.info(
                        "Refreshed creator profile %s (%s)",
                        creator.id,
                        creator.username,
                    )
                except Exception:
                    logger.exception("Failed to refresh creator %s", creator.id)

        await session.commit()


@celery_app.task(name="backend.workers.creator_sync.refresh_creator_profiles")
@async_task
async def refresh_creator_profiles() -> None:
    await _refresh_creator_profiles()
