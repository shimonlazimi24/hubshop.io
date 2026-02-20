"""Tests for SearchKeywordService — recommend, discover, negative keyword CRUD, campaign health."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.search_keyword_service import (
    SearchKeywordService,
)


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
        "backend.modules.advertising.services.search_keyword_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestRecommendKeywords:
    @pytest.mark.asyncio
    async def test_recommend_keywords(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"keyword": "running shoes", "volume": 50000},
                ]
            }
        }

        service = SearchKeywordService(mock_session)
        result = await service.recommend_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword="shoes",
        )

        assert len(result["list"]) == 1
        assert result["list"][0]["keyword"] == "running shoes"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["keyword"] == "shoes"

    @pytest.mark.asyncio
    async def test_recommend_keywords_with_pagination(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = SearchKeywordService(mock_session)
        await service.recommend_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword="shoes",
            page=2,
            page_size=10,
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "2"
        assert call_params["page_size"] == "10"


class TestDiscoverKeywords:
    @pytest.mark.asyncio
    async def test_discover_keywords(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"keyword": "sneakers", "competition": "HIGH"},
                    {"keyword": "trainers", "competition": "MEDIUM"},
                ]
            }
        }

        service = SearchKeywordService(mock_session)
        result = await service.discover_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword="shoes",
        )

        assert len(result["list"]) == 2
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["keyword"] == "shoes"

    @pytest.mark.asyncio
    async def test_discover_keywords_with_pagination(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = SearchKeywordService(mock_session)
        await service.discover_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword="shoes",
            page=3,
            page_size=5,
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "3"
        assert call_params["page_size"] == "5"


class TestListNegativeKeywords:
    @pytest.mark.asyncio
    async def test_list_negative_keywords(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"keyword_id": "nk1", "keyword": "free", "match_type": "EXACT"},
                ]
            }
        }

        service = SearchKeywordService(mock_session)
        result = await service.list_negative_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_group_id="ag123",
        )

        assert len(result["list"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["ad_group_id"] == "ag123"

    @pytest.mark.asyncio
    async def test_list_negative_keywords_with_pagination(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = SearchKeywordService(mock_session)
        await service.list_negative_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_group_id="ag123",
            page=2,
            page_size=10,
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "2"
        assert call_params["page_size"] == "10"


class TestCreateNegativeKeyword:
    @pytest.mark.asyncio
    async def test_create_negative_keyword(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"keyword_id": "nk_new", "keyword": "cheap"}
        }

        service = SearchKeywordService(mock_session)
        result = await service.create_negative_keyword(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_group_id="ag123",
            keyword="cheap",
        )

        assert result["keyword_id"] == "nk_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["ad_group_id"] == "ag123"
        assert call_body["keyword"] == "cheap"
        assert call_body["match_type"] == "EXACT"

    @pytest.mark.asyncio
    async def test_create_negative_keyword_with_match_type(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"keyword_id": "nk_broad", "keyword": "cheap shoes"}
        }

        service = SearchKeywordService(mock_session)
        result = await service.create_negative_keyword(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_group_id="ag123",
            keyword="cheap shoes",
            match_type="BROAD",
        )

        assert result["keyword_id"] == "nk_broad"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["match_type"] == "BROAD"


class TestUpdateNegativeKeyword:
    @pytest.mark.asyncio
    async def test_update_negative_keyword(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"keyword_id": "nk1"}}

        service = SearchKeywordService(mock_session)
        result = await service.update_negative_keyword(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword_id="nk1",
            updates={"match_type": "BROAD"},
        )

        assert result["keyword_id"] == "nk1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["keyword_id"] == "nk1"
        assert call_body["match_type"] == "BROAD"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestDeleteNegativeKeyword:
    @pytest.mark.asyncio
    async def test_delete_negative_keyword(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        service = SearchKeywordService(mock_session)
        result = await service.delete_negative_keyword(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword_ids=["nk1", "nk2"],
        )

        assert result == {}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["keyword_ids"] == ["nk1", "nk2"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetCampaignHealth:
    @pytest.mark.asyncio
    async def test_get_campaign_health(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "campaign_id": "c123",
                "health_score": 85,
                "issues": [],
            }
        }

        service = SearchKeywordService(mock_session)
        result = await service.get_campaign_health(
            sample_ad_account.workspace_id,
            sample_ad_account,
            campaign_id="c123",
        )

        assert result["health_score"] == 85
        assert result["campaign_id"] == "c123"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["campaign_id"] == "c123"
