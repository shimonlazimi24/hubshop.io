"""Tests for SplitTestService — create, update time, end, get results, apply winner."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.split_test_service import SplitTestService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_account_service(
    sample_ad_account: SimpleNamespace, mock_gateway: AsyncMock
):
    with patch(
        "backend.modules.advertising.services.split_test_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestCreateSplitTest:
    @pytest.mark.asyncio
    async def test_create_split_test(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"split_test_id": "st_new", "status": "CREATED"}
        }

        test_config = {
            "test_name": "Creative A/B Test",
            "test_type": "CREATIVE",
            "duration_days": 7,
        }

        service = SplitTestService(mock_session)
        result = await service.create_split_test(
            sample_ad_account.workspace_id,
            sample_ad_account,
            test_config=test_config,
        )

        assert result["split_test_id"] == "st_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["test_name"] == "Creative A/B Test"
        assert call_body["test_type"] == "CREATIVE"


class TestUpdateTestTime:
    @pytest.mark.asyncio
    async def test_update_test_time(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"split_test_id": "st1"}}

        service = SplitTestService(mock_session)
        result = await service.update_test_time(
            sample_ad_account.workspace_id,
            sample_ad_account,
            split_test_id="st1",
            updates={"end_time": "2026-03-01"},
        )

        assert result["split_test_id"] == "st1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["split_test_id"] == "st1"
        assert call_body["end_time"] == "2026-03-01"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestEndSplitTest:
    @pytest.mark.asyncio
    async def test_end_split_test(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        service = SplitTestService(mock_session)
        result = await service.end_split_test(
            sample_ad_account.workspace_id,
            sample_ad_account,
            split_test_id="st1",
        )

        assert result == {}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["split_test_id"] == "st1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetResults:
    @pytest.mark.asyncio
    async def test_get_results(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "split_test_id": "st1",
                "winner": "variant_a",
                "metrics": {"ctr": 0.05},
            }
        }

        service = SplitTestService(mock_session)
        result = await service.get_results(
            sample_ad_account.workspace_id,
            sample_ad_account,
            split_test_id="st1",
        )

        assert result["winner"] == "variant_a"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["split_test_id"] == "st1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestApplyWinner:
    @pytest.mark.asyncio
    async def test_apply_winner(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"split_test_id": "st1", "applied": True}
        }

        service = SplitTestService(mock_session)
        result = await service.apply_winner(
            sample_ad_account.workspace_id,
            sample_ad_account,
            split_test_id="st1",
        )

        assert result["applied"] is True
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["split_test_id"] == "st1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
