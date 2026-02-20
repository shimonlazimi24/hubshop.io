"""Tests for LeadService — test leads, download tasks, form libraries/fields, get leads."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.lead_service import LeadService


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
        "backend.modules.advertising.services.lead_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestCreateTestLead:
    @pytest.mark.asyncio
    async def test_create_test_lead(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"test_lead_id": "tl_1", "form_id": "f1"}
        }

        lead_data = {
            "name": "Test User",
            "email": "test@example.com",
        }

        service = LeadService(mock_session)
        result = await service.create_test_lead(
            sample_ad_account.workspace_id,
            sample_ad_account,
            form_id="f1",
            lead_data=lead_data,
        )

        assert result["test_lead_id"] == "tl_1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["form_id"] == "f1"
        assert call_body["name"] == "Test User"


class TestGetTestLead:
    @pytest.mark.asyncio
    async def test_get_test_lead(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"test_lead_id": "tl_1", "status": "DELIVERED"}
        }

        service = LeadService(mock_session)
        result = await service.get_test_lead(
            sample_ad_account.workspace_id,
            sample_ad_account,
            test_lead_id="tl_1",
        )

        assert result["test_lead_id"] == "tl_1"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["test_lead_id"] == "tl_1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


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

        service = LeadService(mock_session)
        result = await service.create_download_task(
            sample_ad_account.workspace_id,
            sample_ad_account,
            form_id="f1",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )

        assert result["task_id"] == "task_1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["form_id"] == "f1"
        assert call_body["start_date"] == "2026-01-01"
        assert call_body["end_date"] == "2026-01-31"


class TestDownloadLeads:
    @pytest.mark.asyncio
    async def test_download_leads(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"download_url": "https://example.com/leads.csv"}
        }

        service = LeadService(mock_session)
        result = await service.download_leads(
            sample_ad_account.workspace_id,
            sample_ad_account,
            task_id="task_1",
        )

        assert "download_url" in result
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["task_id"] == "task_1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetFormLibraries:
    @pytest.mark.asyncio
    async def test_get_form_libraries(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"libraries": [{"library_id": "lib1", "name": "Default"}]}
        }

        service = LeadService(mock_session)
        result = await service.get_form_libraries(
            sample_ad_account.workspace_id,
            sample_ad_account,
        )

        assert len(result["libraries"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetFormFields:
    @pytest.mark.asyncio
    async def test_get_form_fields(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"fields": [{"field_id": "fld1", "label": "Name"}]}
        }

        service = LeadService(mock_session)
        result = await service.get_form_fields(
            sample_ad_account.workspace_id,
            sample_ad_account,
            form_id="f1",
        )

        assert len(result["fields"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["form_id"] == "f1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetLeads:
    @pytest.mark.asyncio
    async def test_get_leads(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [{"lead_id": "l1", "name": "John Doe"}],
                "page_info": {"total": 1},
            }
        }

        service = LeadService(mock_session)
        result = await service.get_leads(
            sample_ad_account.workspace_id,
            sample_ad_account,
            form_id="f1",
            page=1,
            page_size=10,
        )

        assert len(result["list"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["form_id"] == "f1"
        assert call_params["page"] == "1"
        assert call_params["page_size"] == "10"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
