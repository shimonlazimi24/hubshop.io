"""Tests for CommercialContentService — Ad Library and commercial content queries."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.modules.content.services.commercial_content_service import (
    CommercialContentService,
)


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_account() -> SimpleNamespace:
    return SimpleNamespace(id=uuid.uuid4())


@pytest.fixture
def service(
    mock_account: SimpleNamespace, mock_gateway: AsyncMock
) -> CommercialContentService:
    session = AsyncMock()
    svc = CommercialContentService(session)
    svc._get_developer_gateway = AsyncMock(return_value=(mock_account, mock_gateway))
    return svc


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def date_range() -> dict:
    return {"min": "20231001", "max": "20231231"}


class TestSearchAds:
    @pytest.mark.asyncio
    async def test_search_ads(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
        date_range: dict,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"ads": [{"id": 1}], "search_id": "abc"}
        }

        result = await service.search_ads(workspace_id, date_range=date_range)

        assert result == {"ads": [{"id": 1}], "search_id": "abc"}
        mock_gateway.post.assert_called_once()
        call_kwargs = mock_gateway.post.call_args
        body = call_kwargs[1]["json_body"]
        assert body["filters"]["ad_published_date_range"] == date_range
        assert body["filters"]["country_code"] == "ALL"
        assert body["max_count"] == 20
        assert "search_term" not in body
        assert "search_id" not in body

    @pytest.mark.asyncio
    async def test_search_ads_with_search_term(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
        date_range: dict,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"ads": []}}

        await service.search_ads(
            workspace_id,
            date_range=date_range,
            search_term="skincare",
        )

        body = mock_gateway.post.call_args[1]["json_body"]
        assert body["search_term"] == "skincare"

    @pytest.mark.asyncio
    async def test_search_ads_with_pagination(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
        date_range: dict,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"ads": [], "search_id": "page2"}}

        await service.search_ads(
            workspace_id,
            date_range=date_range,
            search_id="page1_cursor",
        )

        body = mock_gateway.post.call_args[1]["json_body"]
        assert body["search_id"] == "page1_cursor"


class TestSearchAdvertisers:
    @pytest.mark.asyncio
    async def test_search_advertisers(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"advertisers": [{"business_id": "biz_1", "business_name": "Acme"}]}
        }

        result = await service.search_advertisers(workspace_id, search_term="Acme")

        assert result == {
            "advertisers": [{"business_id": "biz_1", "business_name": "Acme"}]
        }
        call_kwargs = mock_gateway.post.call_args
        assert call_kwargs[0][0] == "/research/adlib/advertiser/query/"
        body = call_kwargs[1]["json_body"]
        assert body["search_term"] == "Acme"
        assert body["max_count"] == 20
        params = call_kwargs[1]["params"]
        assert "business_name" in params["fields"]
        assert "business_id" in params["fields"]


class TestGetAdDetail:
    @pytest.mark.asyncio
    async def test_get_ad_detail(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"ad": {"id": 12345, "status": "active"}}
        }

        result = await service.get_ad_detail(workspace_id, ad_id=12345)

        assert result == {"ad": {"id": 12345, "status": "active"}}
        call_kwargs = mock_gateway.post.call_args
        assert call_kwargs[0][0] == "/research/adlib/ad/detail/"
        body = call_kwargs[1]["json_body"]
        assert body["ad_id"] == 12345


class TestGetAdReport:
    @pytest.mark.asyncio
    async def test_get_ad_report(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
        date_range: dict,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"count_time_series_by_country": [{"country": "US", "count": 100}]}
        }

        result = await service.get_ad_report(
            workspace_id,
            date_range=date_range,
            advertiser_business_ids=["biz_1"],
        )

        assert result == {
            "count_time_series_by_country": [{"country": "US", "count": 100}]
        }
        call_kwargs = mock_gateway.post.call_args
        assert call_kwargs[0][0] == "/research/adlib/ad/report/"
        body = call_kwargs[1]["json_body"]
        assert body["filters"]["ad_published_date_range"] == date_range
        assert body["filters"]["advertiser_business_ids"] == ["biz_1"]
        params = call_kwargs[1]["params"]
        assert params["fields"] == "count_time_series_by_country"


class TestSearchCommercialContent:
    @pytest.mark.asyncio
    async def test_search_commercial_content(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
        date_range: dict,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"commercial_contents": [{"id": "cc_1"}]}
        }

        result = await service.search_commercial_content(
            workspace_id, date_range=date_range
        )

        assert result == {"commercial_contents": [{"id": "cc_1"}]}
        call_kwargs = mock_gateway.post.call_args
        assert call_kwargs[0][0] == "/research/adlib/commercial_content/query/"
        body = call_kwargs[1]["json_body"]
        assert body["filters"]["content_published_date_range"] == date_range
        assert body["max_count"] == 20
        assert "creator_usernames" not in body["filters"]
        assert "creator_country_code" not in body["filters"]

    @pytest.mark.asyncio
    async def test_search_commercial_content_with_creators(
        self,
        service: CommercialContentService,
        mock_gateway: AsyncMock,
        workspace_id: uuid.UUID,
        date_range: dict,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"commercial_contents": []}}

        await service.search_commercial_content(
            workspace_id,
            date_range=date_range,
            creator_usernames=["creator1", "creator2"],
            creator_country_code="US",
        )

        body = mock_gateway.post.call_args[1]["json_body"]
        assert body["filters"]["creator_usernames"] == ["creator1", "creator2"]
        assert body["filters"]["creator_country_code"] == "US"
