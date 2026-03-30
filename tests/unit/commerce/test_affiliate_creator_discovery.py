"""Tests for E1: Affiliate creator discovery and search."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.commerce.services.affiliate_service import AffiliateService


class TestSearchCreators:
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
            shop_id="test_shop_123",
        )

    @pytest.mark.asyncio
    async def test_search_creators_basic(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should call gateway GET /affiliate/202309/seller/creators with page_size."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "creators": [
                    {"creator_id": "c1", "nickname": "Creator One"},
                    {"creator_id": "c2", "nickname": "Creator Two"},
                ]
            }
        }

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            original_build = ss_mod.ShopService.build_gateway_for_shop

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.search_creators(mock_shop, page_size=20)

        mock_gateway.get.assert_awaited_once()
        call_args = mock_gateway.get.call_args
        assert "/affiliate/202309/seller/creators" in call_args[0][0]
        assert "creators" in result

    @pytest.mark.asyncio
    async def test_search_creators_with_category_filter(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should pass category param when provided."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"creators": []}}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            await service.search_creators(mock_shop, category="fashion")

        params = mock_gateway.get.call_args[1].get(
            "params",
            mock_gateway.get.call_args[0][1]
            if len(mock_gateway.get.call_args[0]) > 1
            else {},
        )
        assert params.get("category") == "fashion"

    @pytest.mark.asyncio
    async def test_search_creators_with_min_followers(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should pass min_followers param when provided."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"creators": []}}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            await service.search_creators(mock_shop, min_followers=10000)

        params = mock_gateway.get.call_args[1].get(
            "params",
            mock_gateway.get.call_args[0][1]
            if len(mock_gateway.get.call_args[0]) > 1
            else {},
        )
        assert params.get("min_followers") == "10000"

    @pytest.mark.asyncio
    async def test_search_creators_returns_empty_on_no_data(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should return empty dict when API returns no data key."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.search_creators(mock_shop)

        assert result == {}


class TestGetCreatorPerformance:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_get_creator_performance(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should call gateway with correct creator performance endpoint."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "total_sales": "1500.00",
                "total_orders": 25,
            }
        }

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.get_creator_performance(mock_shop, "creator_123")

        mock_gateway.get.assert_awaited_once_with(
            "/affiliate/202309/seller/creators/creator_123/performance"
        )
        assert result["total_sales"] == "1500.00"

    @pytest.mark.asyncio
    async def test_get_creator_performance_empty(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should return empty dict when no data."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.get_creator_performance(mock_shop, "creator_123")

        assert result == {}


class TestGetCreatorProfile:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_get_creator_profile(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should call gateway with correct creator profile endpoint."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "creator_id": "creator_123",
                "nickname": "TestCreator",
                "followers": 50000,
            }
        }

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.get_creator_profile(mock_shop, "creator_123")

        mock_gateway.get.assert_awaited_once_with(
            "/affiliate/202309/seller/creators/creator_123/profile"
        )
        assert result["creator_id"] == "creator_123"
        assert result["nickname"] == "TestCreator"

    @pytest.mark.asyncio
    async def test_get_creator_profile_empty(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should return empty dict when no data."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.get_creator_profile(mock_shop, "creator_123")

        assert result == {}
