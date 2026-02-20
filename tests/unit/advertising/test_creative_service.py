"""Tests for CreativeService — portfolios, smart text, trending hashtags."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.creative_service import CreativeService


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
        "backend.modules.advertising.services.creative_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestListPortfolios:
    @pytest.mark.asyncio
    async def test_list_portfolios(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [{"portfolio_id": "p1", "name": "Portfolio 1"}],
                "page_info": {"total": 1},
            }
        }

        service = CreativeService(mock_session)
        result = await service.list_portfolios(
            sample_ad_account.workspace_id, sample_ad_account
        )

        assert "list" in result
        assert len(result["list"]) == 1
        mock_gateway.get.assert_called_once()
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id

    @pytest.mark.asyncio
    async def test_list_portfolios_pagination(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = CreativeService(mock_session)
        await service.list_portfolios(
            sample_ad_account.workspace_id,
            sample_ad_account,
            page=3,
            page_size=50,
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "3"
        assert call_params["page_size"] == "50"


class TestCreatePortfolio:
    @pytest.mark.asyncio
    async def test_create_portfolio(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"portfolio_id": "p_new", "portfolio_name": "My Portfolio"}
        }

        service = CreativeService(mock_session)
        result = await service.create_portfolio(
            sample_ad_account.workspace_id,
            sample_ad_account,
            name="My Portfolio",
        )

        assert result["portfolio_id"] == "p_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["portfolio_name"] == "My Portfolio"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestGenerateSmartText:
    @pytest.mark.asyncio
    async def test_generate_smart_text(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {
                "suggestions": [
                    {"text": "Shop now and save!"},
                    {"text": "Limited time offer!"},
                ]
            }
        }

        service = CreativeService(mock_session)
        result = await service.generate_smart_text(
            sample_ad_account.workspace_id,
            sample_ad_account,
            params={"industry": "ecommerce", "language": "en"},
        )

        assert len(result["suggestions"]) == 2
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["industry"] == "ecommerce"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetTrendingHashtags:
    @pytest.mark.asyncio
    async def test_get_trending_hashtags(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "hashtags": [
                    {"name": "#trending", "views": 1000000},
                    {"name": "#viral", "views": 500000},
                ]
            }
        }

        service = CreativeService(mock_session)
        result = await service.get_trending_hashtags(
            sample_ad_account.workspace_id, sample_ad_account
        )

        assert len(result["hashtags"]) == 2
        assert result["hashtags"][0]["name"] == "#trending"

    @pytest.mark.asyncio
    async def test_get_trending_hashtags_empty(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"hashtags": []}}

        service = CreativeService(mock_session)
        result = await service.get_trending_hashtags(
            sample_ad_account.workspace_id, sample_ad_account
        )

        assert result["hashtags"] == []
