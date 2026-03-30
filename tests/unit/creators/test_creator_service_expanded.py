"""Expanded tests for CreatorCampaignService and CreatorService — consolidation."""

import os
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.creators.services.campaign_service import CreatorCampaignService
from backend.modules.creators.services.creator_service import CreatorService

# ---------------------------------------------------------------------------
# update_invitation_status
# ---------------------------------------------------------------------------


class TestUpdateInvitationStatus:
    @pytest.mark.asyncio
    async def test_update_invitation_status_accepted(self) -> None:
        invitation = SimpleNamespace(
            id=uuid.uuid4(),
            status="PENDING",
            responded_at=None,
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = invitation
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        updated = await service.update_invitation_status(
            invitation.id, status="ACCEPTED"
        )

        assert updated is not None
        assert updated.status == "ACCEPTED"

    @pytest.mark.asyncio
    async def test_update_invitation_status_declined(self) -> None:
        invitation = SimpleNamespace(
            id=uuid.uuid4(),
            status="PENDING",
            responded_at=None,
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = invitation
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        updated = await service.update_invitation_status(
            invitation.id, status="DECLINED"
        )

        assert updated is not None
        assert updated.status == "DECLINED"

    @pytest.mark.asyncio
    async def test_update_invitation_status_with_responded_at(self) -> None:
        invitation = SimpleNamespace(
            id=uuid.uuid4(),
            status="PENDING",
            responded_at=None,
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = invitation
        session.execute.return_value = result

        now = datetime.now(tz=UTC)
        service = CreatorCampaignService(session)
        updated = await service.update_invitation_status(
            invitation.id, status="ACCEPTED", responded_at=now
        )

        assert updated is not None
        assert updated.status == "ACCEPTED"
        assert updated.responded_at == now

    @pytest.mark.asyncio
    async def test_update_invitation_nonexistent(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        updated = await service.update_invitation_status(
            uuid.uuid4(), status="ACCEPTED"
        )

        assert updated is None


# ---------------------------------------------------------------------------
# get_campaign_stats
# ---------------------------------------------------------------------------


class TestGetCampaignStats:
    @pytest.mark.asyncio
    async def test_campaign_stats_mixed(self) -> None:
        campaign_id = uuid.uuid4()
        invitations = [
            SimpleNamespace(status="PENDING", offered_amount="100"),
            SimpleNamespace(status="ACCEPTED", offered_amount="200"),
            SimpleNamespace(status="DECLINED", offered_amount="150"),
            SimpleNamespace(status="ACCEPTED", offered_amount=None),
        ]
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = invitations
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        stats = await service.get_campaign_stats(campaign_id)

        assert stats["total_invitations"] == 4
        assert stats["pending"] == 1
        assert stats["accepted"] == 2
        assert stats["declined"] == 1
        assert stats["total_offered_amount"] == "450.0"
        assert stats["acceptance_rate"] == 50.0

    @pytest.mark.asyncio
    async def test_campaign_stats_empty(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        stats = await service.get_campaign_stats(uuid.uuid4())

        assert stats["total_invitations"] == 0
        assert stats["pending"] == 0
        assert stats["accepted"] == 0
        assert stats["declined"] == 0
        assert stats["total_offered_amount"] is None
        assert stats["acceptance_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_campaign_stats_acceptance_rate(self) -> None:
        invitations = [
            SimpleNamespace(status="ACCEPTED", offered_amount="500"),
            SimpleNamespace(status="ACCEPTED", offered_amount="300"),
            SimpleNamespace(status="PENDING", offered_amount="200"),
        ]
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = invitations
        session.execute.return_value = result

        service = CreatorCampaignService(session)
        stats = await service.get_campaign_stats(uuid.uuid4())

        # 2 accepted out of 3 = 66.67%
        assert stats["acceptance_rate"] == 66.67
        assert stats["total_offered_amount"] == "1000.0"


# ---------------------------------------------------------------------------
# sync_creator_to_workspace
# ---------------------------------------------------------------------------


class TestSyncCreatorToWorkspace:
    @pytest.mark.asyncio
    async def test_sync_creator_to_workspace(self) -> None:
        workspace_id = uuid.uuid4()
        creator_data = {
            "creator_id": "12345",
            "username": "test_creator",
            "display_name": "Test Creator",
            "follower_count": 50000,
        }
        mock_profile = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            platform_creator_id="12345",
            username="test_creator",
        )

        session = AsyncMock()
        service = CreatorService(session)

        with patch(
            "backend.modules.creators.services.creator_profile_service.CreatorProfileService"
        ) as mock_cls:
            mock_instance = MagicMock()
            mock_instance.upsert_creator_from_api = AsyncMock(return_value=mock_profile)
            mock_cls.return_value = mock_instance

            result = await service.sync_creator_to_workspace(workspace_id, creator_data)

        assert result is mock_profile
        mock_cls.assert_called_once_with(session)

    @pytest.mark.asyncio
    async def test_sync_creator_to_workspace_upsert(self) -> None:
        workspace_id = uuid.uuid4()
        creator_data = {
            "creator_id": "67890",
            "username": "another_creator",
            "follower_count": 100000,
        }
        mock_profile = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            platform_creator_id="67890",
        )

        session = AsyncMock()
        service = CreatorService(session)

        with patch(
            "backend.modules.creators.services.creator_profile_service.CreatorProfileService"
        ) as mock_cls:
            mock_instance = MagicMock()
            mock_instance.upsert_creator_from_api = AsyncMock(return_value=mock_profile)
            mock_cls.return_value = mock_instance

            result = await service.sync_creator_to_workspace(workspace_id, creator_data)

        mock_instance.upsert_creator_from_api.assert_called_once_with(
            workspace_id, creator_data
        )
        assert result.platform_creator_id == "67890"


# ---------------------------------------------------------------------------
# partnership_service removed
# ---------------------------------------------------------------------------


class TestPartnershipServiceRemoved:
    def test_partnership_service_removed(self) -> None:
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "backend",
            "modules",
            "creators",
            "services",
            "partnership_service.py",
        )
        assert not os.path.exists(path), (
            f"partnership_service.py should have been deleted but still exists at {path}"
        )
