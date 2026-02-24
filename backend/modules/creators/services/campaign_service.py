import logging
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.creators import CreatorCampaign, CreatorInvitation
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CreatorCampaignService:
    """Service for creator campaigns and invitations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- Campaigns ---

    async def list_campaigns(
        self,
        workspace_id: uuid.UUID,
        *,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[CreatorCampaign]:
        query = select(CreatorCampaign).where(
            CreatorCampaign.workspace_id == workspace_id
        )
        count_query = select(func.count(CreatorCampaign.id)).where(
            CreatorCampaign.workspace_id == workspace_id
        )

        if status_filter:
            query = query.where(CreatorCampaign.status == status_filter)
            count_query = count_query.where(CreatorCampaign.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(CreatorCampaign.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def get_campaign(self, campaign_id: uuid.UUID) -> CreatorCampaign | None:
        result = await self._session.execute(
            select(CreatorCampaign).where(CreatorCampaign.id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def create_campaign(
        self,
        workspace_id: uuid.UUID,
        *,
        name: str,
        description: str | None = None,
        budget: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        target_categories: list[str] | None = None,
        requirements: dict | None = None,
    ) -> CreatorCampaign:
        campaign = CreatorCampaign(
            workspace_id=workspace_id,
            name=name,
            description=description,
            status="DRAFT",
            budget=budget,
            target_categories=target_categories,
            requirements=requirements,
        )
        if start_date:
            campaign.start_date = datetime.fromisoformat(start_date)
        if end_date:
            campaign.end_date = datetime.fromisoformat(end_date)

        self._session.add(campaign)
        await self._session.flush()
        return campaign

    async def update_campaign(
        self,
        campaign: CreatorCampaign,
        *,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        budget: str | None = None,
    ) -> CreatorCampaign:
        if name:
            campaign.name = name
        if description is not None:
            campaign.description = description
        if status:
            campaign.status = status
        if budget is not None:
            campaign.budget = budget
        return campaign

    # --- Invitations ---

    async def invite_creator(
        self,
        campaign_id: uuid.UUID,
        creator_id: uuid.UUID,
        *,
        message: str | None = None,
        offered_amount: str | None = None,
    ) -> CreatorInvitation:
        invitation = CreatorInvitation(
            campaign_id=campaign_id,
            creator_id=creator_id,
            status="PENDING",
            message=message,
            offered_amount=offered_amount,
        )
        self._session.add(invitation)
        await self._session.flush()
        return invitation

    async def list_invitations(
        self,
        campaign_id: uuid.UUID,
        *,
        status_filter: str | None = None,
    ) -> list[CreatorInvitation]:
        query = select(CreatorInvitation).where(
            CreatorInvitation.campaign_id == campaign_id
        )

        if status_filter:
            query = query.where(CreatorInvitation.status == status_filter)

        result = await self._session.execute(
            query.order_by(CreatorInvitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_invitation_status(
        self,
        invitation_id: uuid.UUID,
        *,
        status: str,
        responded_at: datetime | None = None,
    ) -> CreatorInvitation | None:
        """Update invitation status (ACCEPTED, DECLINED, EXPIRED)."""
        result = await self._session.execute(
            select(CreatorInvitation).where(CreatorInvitation.id == invitation_id)
        )
        invitation = result.scalar_one_or_none()
        if invitation:
            invitation.status = status
            if responded_at:
                invitation.responded_at = responded_at
        return invitation

    async def get_campaign_stats(self, campaign_id: uuid.UUID) -> dict:
        """Get invitation stats for a campaign."""
        result = await self._session.execute(
            select(CreatorInvitation).where(
                CreatorInvitation.campaign_id == campaign_id
            )
        )
        invitations = list(result.scalars().all())

        total = len(invitations)
        pending = sum(1 for i in invitations if i.status == "PENDING")
        accepted = sum(1 for i in invitations if i.status == "ACCEPTED")
        declined = sum(1 for i in invitations if i.status == "DECLINED")

        total_offered = sum(
            float(i.offered_amount) for i in invitations if i.offered_amount
        )
        acceptance_rate = (accepted / total * 100) if total > 0 else 0.0

        return {
            "total_invitations": total,
            "pending": pending,
            "accepted": accepted,
            "declined": declined,
            "total_offered_amount": str(total_offered) if total_offered else None,
            "acceptance_rate": round(acceptance_rate, 2),
        }
