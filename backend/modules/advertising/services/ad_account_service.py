import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class AdAccountService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ad_accounts(self, workspace_id: uuid.UUID) -> list[AdAccount]:
        result = await self._session.execute(
            select(AdAccount)
            .where(AdAccount.workspace_id == workspace_id)
            .order_by(AdAccount.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_ad_account(self, ad_account_id: uuid.UUID) -> AdAccount | None:
        result = await self._session.execute(
            select(AdAccount).where(AdAccount.id == ad_account_id)
        )
        return result.scalar_one_or_none()

    async def get_ad_account_by_advertiser_id(
        self, advertiser_id: str
    ) -> AdAccount | None:
        result = await self._session.execute(
            select(AdAccount).where(AdAccount.advertiser_id == advertiser_id)
        )
        return result.scalar_one_or_none()

    async def sync_ad_accounts_from_connected(
        self, workspace_id: uuid.UUID
    ) -> list[AdAccount]:
        """Discover advertiser accounts from connected Marketing accounts."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.MARKETING,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        accounts = result.scalars().all()
        synced: list[AdAccount] = []

        for account in accounts:
            try:
                gateway = await self.build_gateway(account)
                advertiser_ids = self._extract_advertiser_ids(account)

                if not advertiser_ids:
                    # Use the platform_account_id as fallback
                    advertiser_ids = [account.platform_account_id]

                for adv_id in advertiser_ids:
                    resp = await gateway.get(
                        "/advertiser/info/",
                        params={"advertiser_ids": f'["{adv_id}"]'},
                    )
                    adv_list = resp.get("data", {}).get("list", [])
                    for adv_data in adv_list:
                        ad_account = await self._upsert_ad_account(
                            workspace_id=workspace_id,
                            connected_account_id=account.id,
                            adv_data=adv_data,
                        )
                        synced.append(ad_account)
            except Exception:
                logger.exception(
                    "Failed to sync ad accounts for connected account %s",
                    account.id,
                )

        return synced

    async def build_gateway(self, account: ConnectedAccount) -> PlatformGateway:
        """Build a PlatformGateway for a connected Marketing account."""
        result = await self._session.execute(
            select(TokenVault).where(TokenVault.connected_account_id == account.id)
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokMarketingClient(access_token=access_token)
        return PlatformGateway(
            platform=Platform.MARKETING,
            account_id=str(account.id),
            client=client,
        )

    async def build_gateway_for_ad_account(
        self, ad_account: AdAccount
    ) -> PlatformGateway:
        """Build a PlatformGateway scoped to a specific ad account."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.id == ad_account.connected_account_id
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise ValueError(f"No connected account for ad account {ad_account.id}")
        return await self.build_gateway(account)

    def _extract_advertiser_ids(self, account: ConnectedAccount) -> list[str]:
        """Extract advertiser IDs from connected account metadata."""
        metadata = account.metadata_json or {}
        adv_ids = metadata.get("advertiser_ids", [])
        if isinstance(adv_ids, list):
            return [str(aid) for aid in adv_ids]
        return []

    async def _upsert_ad_account(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        adv_data: dict,
    ) -> AdAccount:
        advertiser_id = str(adv_data.get("advertiser_id", ""))
        existing = await self.get_ad_account_by_advertiser_id(advertiser_id)

        if existing:
            existing.advertiser_name = adv_data.get(
                "advertiser_name", existing.advertiser_name
            )
            existing.currency = adv_data.get("currency", existing.currency)
            existing.timezone = adv_data.get("timezone", existing.timezone)
            return existing

        ad_account = AdAccount(
            workspace_id=workspace_id,
            connected_account_id=connected_account_id,
            advertiser_id=advertiser_id,
            advertiser_name=adv_data.get("advertiser_name", ""),
            currency=adv_data.get("currency"),
            timezone=adv_data.get("timezone"),
        )
        self._session.add(ad_account)
        await self._session.flush()
        return ad_account
