"""Tests for E2: Affiliate sample management."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.commerce.services.affiliate_service import AffiliateService


class TestListSampleRequests:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_list_sample_requests_basic(self, mock_session: AsyncMock) -> None:
        """Should return paginated sample requests for workspace."""
        from backend.db.models.affiliate import SampleRequest

        workspace_id = uuid.uuid4()
        sample = MagicMock(spec=SampleRequest)
        sample.id = uuid.uuid4()
        sample.workspace_id = workspace_id
        sample.status = "PENDING"

        # Mock count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1
        # Mock items query
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [sample]

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_sample_requests(workspace_id)

        assert result.total == 1
        assert result.page == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_list_sample_requests_with_status_filter(
        self, mock_session: AsyncMock
    ) -> None:
        """Should filter by status when provided."""
        workspace_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_sample_requests(
            workspace_id, status_filter="APPROVED"
        )

        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_list_sample_requests_with_shop_filter(
        self, mock_session: AsyncMock
    ) -> None:
        """Should filter by shop_id when provided."""
        workspace_id = uuid.uuid4()
        shop_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_sample_requests(workspace_id, shop_id=shop_id)

        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_sample_requests_pagination(
        self, mock_session: AsyncMock
    ) -> None:
        """Should respect page and page_size parameters."""
        workspace_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 50
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_sample_requests(workspace_id, page=3, page_size=10)

        assert result.total == 50
        assert result.page == 3
        assert result.page_size == 10
        assert result.total_pages == 5


class TestReviewSample:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_approve_sample(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should call gateway to approve sample request."""
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"status": "APPROVED"}}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.review_sample(mock_shop, "req_123", approved=True)

        mock_gateway.post.assert_awaited_once()
        call_args = mock_gateway.post.call_args
        assert "/affiliate/202309/seller/samples/req_123/review" in call_args[0][0]
        assert result["status"] == "APPROVED"

    @pytest.mark.asyncio
    async def test_reject_sample_with_reason(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should pass rejection reason when rejecting."""
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"status": "REJECTED"}}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.review_sample(
                mock_shop,
                "req_456",
                approved=False,
                reason="Product out of stock",
            )

        call_kwargs = mock_gateway.post.call_args[1]
        body = call_kwargs.get("json_body", {})
        assert body.get("approved") is False
        assert body.get("reason") == "Product out of stock"


class TestSampleRequestModel:
    def test_sample_request_model_exists(self) -> None:
        """SampleRequest model should be importable."""
        from backend.db.models.affiliate import SampleRequest

        assert SampleRequest.__tablename__ == "sample_requests"

    def test_sample_request_in_init(self) -> None:
        """SampleRequest should be exported from models __init__."""
        from backend.db.models import SampleRequest

        assert SampleRequest is not None
