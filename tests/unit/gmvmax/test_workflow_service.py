"""Tests for GmvMaxWorkflowService — draft CRUD, linking, deep link generation."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.gmvmax import CampaignType, DraftStatus, GmvMaxDraft
from backend.modules.gmvmax.schemas import (
    CreateDraftRequest,
    DeepLinkResponse,
    DraftResponse,
    LinkDraftRequest,
)
from backend.modules.gmvmax.services.workflow_service import GmvMaxWorkflowService


class TestCreateDraft:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_creates_draft_with_product_type(
        self, mock_session: AsyncMock
    ) -> None:
        service = GmvMaxWorkflowService(mock_session)
        workspace_id = uuid.uuid4()
        user_id = uuid.uuid4()
        request = CreateDraftRequest(
            campaign_type="PRODUCT",
            product_ids=["prod_1", "prod_2"],
            daily_budget=100.00,
            roi_target=3.5,
            notes="Test draft",
        )

        draft = await service.create_draft(
            workspace_id=workspace_id,
            user_id=user_id,
            request=request,
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        assert draft.workspace_id == workspace_id
        assert draft.campaign_type == CampaignType.PRODUCT
        assert draft.status == DraftStatus.DRAFT
        assert draft.created_by == user_id

    @pytest.mark.asyncio
    async def test_creates_draft_with_live_type(self, mock_session: AsyncMock) -> None:
        service = GmvMaxWorkflowService(mock_session)
        request = CreateDraftRequest(
            campaign_type="LIVE",
            daily_budget=50.00,
        )

        draft = await service.create_draft(
            workspace_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            request=request,
        )

        assert draft.campaign_type == CampaignType.LIVE

    @pytest.mark.asyncio
    async def test_rejects_invalid_campaign_type(self, mock_session: AsyncMock) -> None:
        service = GmvMaxWorkflowService(mock_session)
        request = CreateDraftRequest(
            campaign_type="INVALID",
            daily_budget=100.00,
        )

        with pytest.raises(ValueError, match="Invalid campaign_type"):
            await service.create_draft(
                workspace_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                request=request,
            )


class TestGetDraft:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_returns_draft_when_found(self, mock_session: AsyncMock) -> None:
        draft_id = uuid.uuid4()
        fake_draft = GmvMaxDraft(
            id=draft_id,
            workspace_id=uuid.uuid4(),
            campaign_type=CampaignType.PRODUCT,
            daily_budget=Decimal("100.00"),
            status=DraftStatus.DRAFT,
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = fake_draft
        mock_session.execute.return_value = result_mock

        service = GmvMaxWorkflowService(mock_session)
        result = await service.get_draft(draft_id)

        assert result is not None
        assert result.id == draft_id

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, mock_session: AsyncMock) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        service = GmvMaxWorkflowService(mock_session)
        result = await service.get_draft(uuid.uuid4())

        assert result is None


class TestListDrafts:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_returns_paginated_result(self, mock_session: AsyncMock) -> None:
        workspace_id = uuid.uuid4()

        # Mock count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        # Mock items query
        items_result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [
            GmvMaxDraft(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                campaign_type=CampaignType.PRODUCT,
                daily_budget=Decimal("100.00"),
                status=DraftStatus.DRAFT,
            ),
            GmvMaxDraft(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                campaign_type=CampaignType.LIVE,
                daily_budget=Decimal("200.00"),
                status=DraftStatus.LINKED,
            ),
        ]
        items_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, items_result]

        service = GmvMaxWorkflowService(mock_session)
        result = await service.list_drafts(
            workspace_id=workspace_id,
            page=1,
            page_size=20,
        )

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 20

    @pytest.mark.asyncio
    async def test_filters_by_status(self, mock_session: AsyncMock) -> None:
        workspace_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        items_result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [
            GmvMaxDraft(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                campaign_type=CampaignType.PRODUCT,
                daily_budget=Decimal("100.00"),
                status=DraftStatus.LINKED,
            ),
        ]
        items_result.scalars.return_value = scalars_mock

        mock_session.execute.side_effect = [count_result, items_result]

        service = GmvMaxWorkflowService(mock_session)
        result = await service.list_drafts(
            workspace_id=workspace_id,
            page=1,
            page_size=20,
            status_filter=DraftStatus.LINKED,
        )

        assert result.total == 1
        assert len(result.items) == 1


class TestLinkDraft:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_links_draft_to_campaign(self, mock_session: AsyncMock) -> None:
        draft_id = uuid.uuid4()
        fake_draft = GmvMaxDraft(
            id=draft_id,
            workspace_id=uuid.uuid4(),
            campaign_type=CampaignType.PRODUCT,
            daily_budget=Decimal("100.00"),
            status=DraftStatus.DRAFT,
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = fake_draft
        mock_session.execute.return_value = result_mock

        service = GmvMaxWorkflowService(mock_session)
        request = LinkDraftRequest(ads_manager_campaign_id="camp_123")
        result = await service.link_draft(draft_id, request)

        assert result is not None
        assert result.ads_manager_campaign_id == "camp_123"
        assert result.status == DraftStatus.LINKED
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_draft_not_found(
        self, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        service = GmvMaxWorkflowService(mock_session)
        request = LinkDraftRequest(ads_manager_campaign_id="camp_123")
        result = await service.link_draft(uuid.uuid4(), request)

        assert result is None


class TestGenerateDeepLink:
    def test_product_deep_link(self) -> None:
        session = AsyncMock()
        service = GmvMaxWorkflowService(session)
        result = service.generate_deep_link(CampaignType.PRODUCT)

        assert isinstance(result, str)
        assert "PRODUCT" in result
        assert "ads.tiktok.com" in result

    def test_live_deep_link(self) -> None:
        session = AsyncMock()
        service = GmvMaxWorkflowService(session)
        result = service.generate_deep_link(CampaignType.LIVE)

        assert isinstance(result, str)
        assert "LIVE" in result
        assert "ads.tiktok.com" in result


class TestSchemas:
    """Test Pydantic schema validation."""

    def test_create_draft_request_minimal(self) -> None:
        req = CreateDraftRequest(campaign_type="PRODUCT", daily_budget=100.00)
        assert req.campaign_type == "PRODUCT"
        assert req.daily_budget == 100.00
        assert req.product_ids is None
        assert req.roi_target is None
        assert req.notes is None

    def test_create_draft_request_full(self) -> None:
        req = CreateDraftRequest(
            campaign_type="LIVE",
            product_ids=["p1", "p2"],
            daily_budget=200.00,
            roi_target=4.0,
            notes="Test",
        )
        assert req.product_ids == ["p1", "p2"]
        assert req.roi_target == 4.0

    def test_link_draft_request(self) -> None:
        req = LinkDraftRequest(ads_manager_campaign_id="camp_456")
        assert req.ads_manager_campaign_id == "camp_456"

    def test_deep_link_response(self) -> None:
        resp = DeepLinkResponse(
            url="https://ads.tiktok.com/...",
            campaign_type="PRODUCT",
        )
        assert resp.url.startswith("https://")

    def test_draft_response_from_attributes(self) -> None:
        assert DraftResponse.model_config.get("from_attributes") is True
