import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Shop
from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.shop.client import TikTokShopClient
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class ShopService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_shops(self, workspace_id: uuid.UUID) -> list[Shop]:
        result = await self._session.execute(
            select(Shop)
            .where(Shop.workspace_id == workspace_id)
            .order_by(Shop.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_shop(self, shop_id: uuid.UUID) -> Shop | None:
        result = await self._session.execute(
            select(Shop).where(Shop.id == shop_id)
        )
        return result.scalar_one_or_none()

    async def get_shop_by_platform_id(self, platform_shop_id: str) -> Shop | None:
        result = await self._session.execute(
            select(Shop).where(Shop.shop_id == platform_shop_id)
        )
        return result.scalar_one_or_none()

    async def sync_shops_from_connected_accounts(
        self, workspace_id: uuid.UUID
    ) -> list[Shop]:
        """Discover shops from connected Shop accounts and create local mirrors."""
        result = await self._session.execute(
            select(ConnectedAccount)
            .where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.SHOP,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        accounts = result.scalars().all()
        synced: list[Shop] = []

        for account in accounts:
            try:
                gateway = await self._build_gateway(account)
                resp = await gateway.get("/authorization/202309/shops")
                shops_data = resp.get("data", {}).get("shops", [])

                for shop_data in shops_data:
                    shop = await self._upsert_shop(
                        workspace_id=workspace_id,
                        connected_account_id=account.id,
                        shop_data=shop_data,
                    )
                    synced.append(shop)
            except Exception:
                logger.exception(
                    "Failed to sync shops for account %s", account.id
                )

        return synced

    async def _upsert_shop(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        shop_data: dict,
    ) -> Shop:
        platform_shop_id = str(shop_data["id"])
        existing = await self.get_shop_by_platform_id(platform_shop_id)

        if existing:
            existing.shop_name = shop_data.get("shop_name", existing.shop_name)
            existing.shop_cipher = shop_data.get("cipher", existing.shop_cipher)
            existing.region = shop_data.get("region", existing.region)
            return existing

        shop = Shop(
            workspace_id=workspace_id,
            connected_account_id=connected_account_id,
            shop_id=platform_shop_id,
            shop_cipher=shop_data.get("cipher", ""),
            shop_name=shop_data.get("shop_name", ""),
            region=shop_data.get("region", ""),
        )
        self._session.add(shop)
        await self._session.flush()
        return shop

    async def _build_gateway(
        self, account: ConnectedAccount
    ) -> PlatformGateway:
        """Build a PlatformGateway for a connected Shop account."""
        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == account.id
            )
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokShopClient(access_token=access_token)
        return PlatformGateway(
            platform=Platform.SHOP,
            account_id=str(account.id),
            client=client,
        )

    async def build_gateway_for_shop(self, shop: Shop) -> PlatformGateway:
        """Build a PlatformGateway scoped to a specific shop."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.id == shop.connected_account_id
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise ValueError(f"No connected account for shop {shop.id}")

        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == account.id
            )
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokShopClient(
            access_token=access_token,
            shop_cipher=shop.shop_cipher,
        )
        return PlatformGateway(
            platform=Platform.SHOP,
            account_id=str(account.id),
            client=client,
        )
