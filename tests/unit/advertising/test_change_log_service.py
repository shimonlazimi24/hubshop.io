"""Tests for ChangeLogService — create download task, get status, download file."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.change_log_service import ChangeLogService


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
        "backend.modules.advertising.services.change_log_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestCreateDownloadTask:
    @pytest.mark.asyncio
    async def test_create_download_task(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"task_id": "task_1", "status": "PENDING"}
        }

        service = ChangeLogService(mock_session)
        result = await service.create_download_task(
            sample_ad_account.workspace_id,
            sample_ad_account,
            object_type="CAMPAIGN",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )

        assert result["task_id"] == "task_1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["object_type"] == "CAMPAIGN"
        assert call_body["start_date"] == "2026-01-01"
        assert call_body["end_date"] == "2026-01-31"


class TestGetTaskStatus:
    @pytest.mark.asyncio
    async def test_get_task_status(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"task_id": "task_1", "status": "COMPLETED"}
        }

        service = ChangeLogService(mock_session)
        result = await service.get_task_status(
            sample_ad_account.workspace_id,
            sample_ad_account,
            task_id="task_1",
        )

        assert result["status"] == "COMPLETED"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["task_id"] == "task_1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestDownloadFile:
    @pytest.mark.asyncio
    async def test_download_file(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"download_url": "https://example.com/changelog.csv"}
        }

        service = ChangeLogService(mock_session)
        result = await service.download_file(
            sample_ad_account.workspace_id,
            sample_ad_account,
            task_id="task_1",
        )

        assert "download_url" in result
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["task_id"] == "task_1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
