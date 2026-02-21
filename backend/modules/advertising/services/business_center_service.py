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

    # --- Partner Management ---

    async def list_partners(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List partners of a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/partner/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def add_partner(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        partner_bc_id: str,
        relationship_type: str = "PARTNER",
    ) -> dict:
        """Add a partner to a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/partner/add/",
            json_body={
                "bc_id": bc_id,
                "partner_bc_id": partner_bc_id,
                "relationship_type": relationship_type,
            },
        )
        return resp.get("data", {})

    async def delete_partner(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        partner_bc_id: str,
    ) -> dict:
        """Remove a partner from a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/partner/delete/",
            json_body={
                "bc_id": bc_id,
                "partner_bc_id": partner_bc_id,
            },
        )
        return resp.get("data", {})

    async def get_partner_assets(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        partner_bc_id: str,
    ) -> dict:
        """Get assets shared with a partner."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/partner/asset/get/",
            params={
                "bc_id": bc_id,
                "partner_bc_id": partner_bc_id,
            },
        )
        return resp.get("data", {})

    # --- Asset Management ---

    async def list_assets(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        asset_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List assets in a Business Center."""
        gateway = await self._get_gateway(ad_account)
        params: dict[str, str] = {
            "bc_id": bc_id,
            "page": str(page),
            "page_size": str(page_size),
        }
        if asset_type is not None:
            params["asset_type"] = asset_type
        resp = await gateway.get(
            "/bc/asset/get/",
            params=params,
        )
        return resp.get("data", {})

    async def assign_asset(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        asset_ids: list[str],
        member_ids: list[str],
    ) -> dict:
        """Assign assets to members in a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/asset/assign/",
            json_body={
                "bc_id": bc_id,
                "asset_ids": asset_ids,
                "member_ids": member_ids,
            },
        )
        return resp.get("data", {})

    async def unassign_asset(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        asset_ids: list[str],
        member_ids: list[str],
    ) -> dict:
        """Unassign assets from members in a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/asset/unassign/",
            json_body={
                "bc_id": bc_id,
                "asset_ids": asset_ids,
                "member_ids": member_ids,
            },
        )
        return resp.get("data", {})

    async def create_ad_account_in_bc(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        advertiser_name: str,
        timezone: str,
        currency: str,
        industry_id: str | None = None,
    ) -> dict:
        """Create a new ad account within a Business Center."""
        gateway = await self._get_gateway(ad_account)
        body: dict[str, str] = {
            "bc_id": bc_id,
            "advertiser_name": advertiser_name,
            "timezone": timezone,
            "currency": currency,
        }
        if industry_id is not None:
            body["industry_id"] = industry_id
        resp = await gateway.post(
            "/bc/asset/ad_account/create/",
            json_body=body,
        )
        return resp.get("data", {})

    # --- Finance (Payments, Billing, Invoices) ---

    async def get_bc_balance(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
    ) -> dict:
        """Get the payment balance for a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/payment/balance/get/",
            params={"bc_id": bc_id},
        )
        return resp.get("data", {})

    async def process_payment(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        advertiser_id: str,
        transfer_type: str,
        amount: float,
    ) -> dict:
        """Process a fund transfer (GRANT or RECLAIM) within a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/bc/payment/process/",
            json_body={
                "bc_id": bc_id,
                "advertiser_id": advertiser_id,
                "transfer_type": transfer_type,
                "amount": amount,
            },
        )
        return resp.get("data", {})

    async def list_transactions(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List transaction records for a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/payment/transaction/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def list_billing_groups(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List billing groups for a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/billing_group/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_billing_group(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        billing_group_name: str,
        advertiser_ids: list[str] | None = None,
    ) -> dict:
        """Create a billing group in a Business Center."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "bc_id": bc_id,
            "billing_group_name": billing_group_name,
        }
        if advertiser_ids is not None:
            body["advertiser_ids"] = advertiser_ids
        resp = await gateway.post(
            "/bc/billing_group/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def list_invoices(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List invoices for a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/invoice/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_cost_records(
        self,
        ad_account: AdAccount,
        *,
        bc_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get cost records for a Business Center."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/bc/payment/cost/get/",
            params={
                "bc_id": bc_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})
