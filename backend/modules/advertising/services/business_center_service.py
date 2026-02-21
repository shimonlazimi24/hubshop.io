import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class BusinessCenterService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_business_centers(
        self,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List Business Centers accessible via the connected account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/get/",
            params={
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_activity_log(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get the activity log for a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/activity_log/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def list_members(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List members of a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/member/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def invite_member(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        emails: list[str],
        role: str,
    ) -> dict:
        """Invite members to a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/member/invite/",
            json_body={
                "bc_id": bc_id,
                "member_emails": emails,
                "role": role,
            },
        )
        return resp.get("data", {})

    async def update_member(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        member_id: str,
        role: str,
    ) -> dict:
        """Update a member's role in a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/member/update/",
            json_body={
                "bc_id": bc_id,
                "member_id": member_id,
                "role": role,
            },
        )
        return resp.get("data", {})

    async def delete_member(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        member_id: str,
    ) -> dict:
        """Remove a member from a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/member/delete/",
            json_body={
                "bc_id": bc_id,
                "member_id": member_id,
            },
        )
        return resp.get("data", {})
