import logging
import uuid
from urllib.parse import urlencode

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.gmvmax import CampaignType, DraftStatus, GmvMaxDraft
from backend.modules.gmvmax.schemas import CreateDraftRequest, LinkDraftRequest
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)

_VALID_CAMPAIGN_TYPES = {ct.value for ct in CampaignType}

_ADS_MANAGER_BASE_URL = "https://ads.tiktok.com/i18n/perf/campaign"


class GmvMaxWorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_draft(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        request: CreateDraftRequest,
    ) -> GmvMaxDraft:
        """Create a new GMV Max draft campaign."""
        if request.campaign_type not in _VALID_CAMPAIGN_TYPES:
            raise ValueError(
                f"Invalid campaign_type: {request.campaign_type}. "
                f"Must be one of {_VALID_CAMPAIGN_TYPES}"
            )

        draft = GmvMaxDraft(
            workspace_id=workspace_id,
            campaign_type=CampaignType(request.campaign_type),
            product_ids=request.product_ids,
            daily_budget=request.daily_budget,
            roi_target=request.roi_target,
            status=DraftStatus.DRAFT,
            created_by=user_id,
            notes=request.notes,
        )
        self._session.add(draft)
        await self._session.flush()
        return draft

    async def get_draft(self, draft_id: uuid.UUID) -> GmvMaxDraft | None:
        """Retrieve a single draft by ID."""
        result = await self._session.execute(
            select(GmvMaxDraft).where(GmvMaxDraft.id == draft_id)
        )
        return result.scalar_one_or_none()

    async def list_drafts(
        self,
        workspace_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status_filter: DraftStatus | None = None,
    ) -> PaginatedResult[GmvMaxDraft]:
        """List drafts with pagination and optional status filter."""
        base_filter = GmvMaxDraft.workspace_id == workspace_id
        if status_filter is not None:
            base_filter = base_filter & (GmvMaxDraft.status == status_filter)

        # Count total
        count_q = select(func.count()).select_from(GmvMaxDraft).where(base_filter)
        total = (await self._session.execute(count_q)).scalar_one()

        # Fetch page
        offset = (page - 1) * page_size
        items_q = (
            select(GmvMaxDraft)
            .where(base_filter)
            .order_by(GmvMaxDraft.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = (await self._session.execute(items_q)).scalars().all()

        return PaginatedResult(
            items=list(items),
            total=total,
            page=page,
            page_size=page_size,
        )

    async def link_draft(
        self,
        draft_id: uuid.UUID,
        request: LinkDraftRequest,
    ) -> GmvMaxDraft | None:
        """Link a draft to an Ads Manager campaign."""
        draft = await self.get_draft(draft_id)
        if draft is None:
            return None

        draft.ads_manager_campaign_id = request.ads_manager_campaign_id
        draft.status = DraftStatus.LINKED
        await self._session.flush()
        return draft

    def generate_deep_link(self, campaign_type: CampaignType) -> str:
        """Return an Ads Manager URL with campaign type parameter."""
        params = urlencode({"campaign_type": campaign_type.value})
        return f"{_ADS_MANAGER_BASE_URL}?{params}"
