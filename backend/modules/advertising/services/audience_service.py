import hashlib
import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, Audience
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class AudienceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_audiences(
        self,
        workspace_id: uuid.UUID,
        *,
        ad_account_id: uuid.UUID | None = None,
        audience_type: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Audience]:
        query = select(Audience).where(Audience.workspace_id == workspace_id)
        count_query = select(func.count(Audience.id)).where(
            Audience.workspace_id == workspace_id
        )

        if ad_account_id:
            query = query.where(Audience.ad_account_id == ad_account_id)
            count_query = count_query.where(Audience.ad_account_id == ad_account_id)
        if audience_type:
            query = query.where(Audience.audience_type == audience_type)
            count_query = count_query.where(Audience.audience_type == audience_type)
        if search:
            query = query.where(Audience.name.ilike(f"%{search}%"))
            count_query = count_query.where(Audience.name.ilike(f"%{search}%"))

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Audience.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_audience(self, audience_id: uuid.UUID) -> Audience | None:
        result = await self._session.execute(
            select(Audience).where(Audience.id == audience_id)
        )
        return result.scalar_one_or_none()

    async def create_custom_audience(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        name: str,
        file_paths: list[str] | None = None,
    ) -> Audience:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "custom_audience_name": name,
        }
        if file_paths:
            body["file_paths"] = file_paths

        resp = await gateway.post("/dmp/custom_audience/create/", json_body=body)
        data = resp.get("data", {})
        platform_id = str(data.get("custom_audience_id", ""))

        audience = Audience(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            platform_audience_id=platform_id,
            name=name,
            audience_type="CUSTOM",
            detail_json=data,
        )
        self._session.add(audience)
        await self._session.flush()
        return audience

    async def create_lookalike_audience(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        name: str,
        source_audience_id: str,
        lookalike_ratio: float = 0.01,
    ) -> Audience:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body = {
            "advertiser_id": ad_account.advertiser_id,
            "custom_audience_name": name,
            "source_audience_id": source_audience_id,
            "lookalike_ratio": lookalike_ratio,
        }

        resp = await gateway.post("/dmp/custom_audience/lookalike/create/", json_body=body)
        data = resp.get("data", {})
        platform_id = str(data.get("custom_audience_id", ""))

        audience = Audience(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            platform_audience_id=platform_id,
            name=name,
            audience_type="LOOKALIKE",
            detail_json=data,
        )
        self._session.add(audience)
        await self._session.flush()
        return audience

    async def delete_audience(
        self, audience: Audience, ad_account: AdAccount
    ) -> None:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        await gateway.post(
            "/dmp/custom_audience/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "custom_audience_ids": [audience.platform_audience_id],
            },
        )
        await self._session.delete(audience)

    async def sync_audiences(self, ad_account: AdAccount) -> int:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        synced = 0
        page = 1

        while True:
            resp = await gateway.get(
                "/dmp/custom_audience/list/",
                params={
                    "advertiser_id": ad_account.advertiser_id,
                    "page": str(page),
                    "page_size": "100",
                },
            )
            data = resp.get("data", {})
            audience_list = data.get("list", [])

            for aud_data in audience_list:
                await self._upsert_audience(ad_account, aud_data)
                synced += 1

            total_page = data.get("page_info", {}).get("total_page", 1)
            if page >= total_page or not audience_list:
                break
            page += 1

        return synced

    async def _upsert_audience(
        self, ad_account: AdAccount, aud_data: dict
    ) -> Audience:
        platform_id = str(aud_data.get("custom_audience_id", ""))
        result = await self._session.execute(
            select(Audience).where(Audience.platform_audience_id == platform_id)
        )
        audience = result.scalar_one_or_none()

        name = aud_data.get("name", "")
        audience_type = "LOOKALIKE" if aud_data.get("is_expiring") else "CUSTOM"
        size = aud_data.get("audience_details", {}).get("audience_size")

        if audience:
            audience.name = name
            audience.audience_type = audience_type
            audience.size = size
            audience.detail_json = aud_data
        else:
            audience = Audience(
                workspace_id=ad_account.workspace_id,
                ad_account_id=ad_account.id,
                platform_audience_id=platform_id,
                name=name,
                audience_type=audience_type,
                size=size,
                detail_json=aud_data,
            )
            self._session.add(audience)
            await self._session.flush()

        return audience

    async def share_audience(
        self,
        workspace_id: uuid.UUID,
        audience_id: uuid.UUID,
        target_advertiser_ids: list[str],
    ) -> dict:
        """Share an audience with other advertiser accounts."""
        audience = await self.get_audience(audience_id)
        if not audience:
            raise ValueError(f"Audience {audience_id} not found")

        account_service = AdAccountService(self._session)
        ad_account = await account_service.get_ad_account(audience.ad_account_id)
        if not ad_account:
            raise ValueError(f"Ad account not found for audience {audience_id}")

        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        resp = await gateway.post(
            "/audience/share/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "custom_audience_ids": [audience.platform_audience_id],
                "target_advertiser_ids": target_advertiser_ids,
            },
        )
        return resp.get("data", {})

    async def get_audience_overlap(
        self,
        workspace_id: uuid.UUID,
        audience_ids: list[uuid.UUID],
    ) -> dict:
        """Get overlap analysis between multiple audiences."""
        if len(audience_ids) < 2:
            raise ValueError("At least 2 audience IDs required for overlap analysis")

        # Resolve platform IDs and get an ad account for gateway
        platform_ids: list[str] = []
        ad_account: AdAccount | None = None
        for aid in audience_ids:
            audience = await self.get_audience(aid)
            if not audience:
                raise ValueError(f"Audience {aid} not found")
            platform_ids.append(audience.platform_audience_id)
            if ad_account is None:
                account_service = AdAccountService(self._session)
                ad_account = await account_service.get_ad_account(
                    audience.ad_account_id
                )

        if not ad_account:
            raise ValueError("No ad account found for audiences")

        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        resp = await gateway.post(
            "/audience/overlap/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "custom_audience_ids": platform_ids,
            },
        )
        return resp.get("data", {})

    async def upload_audience_file(
        self,
        workspace_id: uuid.UUID,
        audience_id: uuid.UUID,
        file_data: list[str],
        hash_type: str = "SHA256",
    ) -> dict:
        """Upload PII data for a custom audience, hashing with SHA-256 before sending."""
        audience = await self.get_audience(audience_id)
        if not audience:
            raise ValueError(f"Audience {audience_id} not found")

        account_service = AdAccountService(self._session)
        ad_account = await account_service.get_ad_account(audience.ad_account_id)
        if not ad_account:
            raise ValueError(f"Ad account not found for audience {audience_id}")

        # SHA-256 hash all PII entries before sending
        hashed_data = [
            hashlib.sha256(entry.strip().lower().encode()).hexdigest()
            for entry in file_data
        ]

        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        resp = await gateway.post(
            "/dmp/custom_audience/file/upload/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "custom_audience_id": audience.platform_audience_id,
                "file_signature": hashed_data,
                "signature_type": hash_type,
            },
        )
        return resp.get("data", {})

    async def create_rule_audience(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        name: str,
        rules: list[dict],
    ) -> Audience:
        """Create a rule-based audience."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "custom_audience_name": name,
            "rules": rules,
        }

        resp = await gateway.post("/audience/rule/create/", json_body=body)
        data = resp.get("data", {})
        platform_id = str(data.get("custom_audience_id", ""))

        audience = Audience(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            platform_audience_id=platform_id,
            name=name,
            audience_type="RULE",
            detail_json=data,
        )
        self._session.add(audience)
        await self._session.flush()
        return audience
