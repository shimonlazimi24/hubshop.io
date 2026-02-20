"""Tests for CreatorCampaignService - campaigns, invitations."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.creators import CreatorCampaign, CreatorInvitation
from backend.modules.creators.services.campaign_service import CreatorCampaignService


class TestListCampaigns:
    @pytest.mark.asyncio
    async def test_list_campaigns_paginated(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        camp1 = SimpleNamespace(
            id=uuid.uuid4(), name="Summer Campaign", status="ACTIVE"
        )
        camp2 = SimpleNamespace(
            id=uuid.uuid4(), name="Winter Campaign", status="DRAFT"
        )
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [camp1, camp2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CreatorCampaignService(session)
        result = await service.list_campaigns(uuid.uuid4(), page=1, page_size=20)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 20

    @pytest.mark.asyncio
    async def test_list_campaigns_empty(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CreatorCampaignService(session)
        result = await service.list_campaigns(uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0


class TestGetCampaign:
    @pytest.mark.asyncio
    async def test_get_campaign_found(self) -> None:
        campaign = SimpleNamespace(
            id=uuid.uuid4(), name="Found Campaign", status="ACTIVE"
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = campaign
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        found = await service.get_campaign(campaign.id)

        assert found is not None
        assert found.name == "Found Campaign"
        assert found.status == "ACTIVE"

    @pytest.mark.asyncio
    async def test_get_campaign_not_found(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        found = await service.get_campaign(uuid.uuid4())

        assert found is None


class TestCreateCampaign:
    @pytest.mark.asyncio
    async def test_create_campaign(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        workspace_id = uuid.uuid4()
        service = CreatorCampaignService(session)
        campaign = await service.create_campaign(
            workspace_id,
            name="New Creator Campaign",
            description="Test campaign for creators",
            budget="5000",
            target_categories=["beauty", "fashion"],
            requirements={"min_followers": 10000},
        )

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert isinstance(added, CreatorCampaign)
        assert added.name == "New Creator Campaign"
        assert added.status == "DRAFT"
        assert added.budget == "5000"
        assert added.workspace_id == workspace_id
        assert added.target_categories == ["beauty", "fashion"]
        assert added.requirements == {"min_followers": 10000}


class TestUpdateCampaign:
    @pytest.mark.asyncio
    async def test_update_campaign_fields(self) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            name="Old Name",
            description="Old desc",
            status="DRAFT",
            budget="1000",
        )
        session = AsyncMock()

        service = CreatorCampaignService(session)
        updated = await service.update_campaign(
            existing,
            name="Updated Name",
            status="ACTIVE",
            budget="7500",
        )

        assert updated.name == "Updated Name"
        assert updated.status == "ACTIVE"
        assert updated.budget == "7500"

    @pytest.mark.asyncio
    async def test_update_campaign_partial(self) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            name="Keep This Name",
            description="Keep desc",
            status="DRAFT",
            budget="2000",
        )
        session = AsyncMock()

        service = CreatorCampaignService(session)
        updated = await service.update_campaign(
            existing,
            status="ACTIVE",
        )

        # name should not change (None is falsy, so the if-guard skips it)
        assert updated.name == "Keep This Name"
        assert updated.status == "ACTIVE"
        assert updated.budget == "2000"


class TestInviteCreator:
    @pytest.mark.asyncio
    async def test_invite_creator(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        campaign_id = uuid.uuid4()
        creator_id = uuid.uuid4()

        service = CreatorCampaignService(session)
        invitation = await service.invite_creator(
            campaign_id,
            creator_id,
            message="We'd love to work with you!",
            offered_amount="500",
        )

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert isinstance(added, CreatorInvitation)
        assert added.campaign_id == campaign_id
        assert added.creator_id == creator_id
        assert added.status == "PENDING"
        assert added.message == "We'd love to work with you!"
        assert added.offered_amount == "500"


class TestListInvitations:
    @pytest.mark.asyncio
    async def test_list_invitations(self) -> None:
        campaign_id = uuid.uuid4()
        inv1 = SimpleNamespace(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            creator_id=uuid.uuid4(),
            status="PENDING",
        )
        inv2 = SimpleNamespace(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            creator_id=uuid.uuid4(),
            status="ACCEPTED",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [inv1, inv2]
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        invitations = await service.list_invitations(campaign_id)

        assert len(invitations) == 2
        assert invitations[0].status == "PENDING"
        assert invitations[1].status == "ACCEPTED"

    @pytest.mark.asyncio
    async def test_list_invitations_empty(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        invitations = await service.list_invitations(uuid.uuid4())

        assert invitations == []
