from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.catalog_service import CatalogService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_ad_account() -> MagicMock:
    account = MagicMock()
    account.advertiser_id = "adv_123"
    return account


@pytest.fixture
def service(mock_session: AsyncMock) -> CatalogService:
    return CatalogService(mock_session)


class TestGetCatalogOverview:
    @pytest.mark.asyncio
    async def test_get_catalog_overview(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"total_products": 150, "active_products": 120}
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_catalog_overview(
                ad_account=mock_ad_account, catalog_id="cat1"
            )
        assert result["total_products"] == 150
        assert result["active_products"] == 120
        mock_gateway.get.assert_called_once_with(
            "/catalog/overview/get/",
            params={"bc_id": "adv_123", "catalog_id": "cat1"},
        )


class TestGetTrendingProducts:
    @pytest.mark.asyncio
    async def test_get_trending_products_default_pagination(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "products": [
                    {"product_id": "p1", "name": "Trending Item A"},
                    {"product_id": "p2", "name": "Trending Item B"},
                ]
            }
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_trending_products(
                ad_account=mock_ad_account, catalog_id="cat1"
            )
        assert len(result["products"]) == 2
        assert result["products"][0]["product_id"] == "p1"
        mock_gateway.get.assert_called_once_with(
            "/catalog/insights/product/trending/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_get_trending_products_custom_pagination(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"products": []}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_trending_products(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                page=2,
                page_size=10,
            )
        assert result["products"] == []
        mock_gateway.get.assert_called_once_with(
            "/catalog/insights/product/trending/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "page": "2",
                "page_size": "10",
            },
        )


class TestGetTrendingCategories:
    @pytest.mark.asyncio
    async def test_get_trending_categories(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "categories": [
                    {"category_id": "c1", "name": "Electronics"},
                    {"category_id": "c2", "name": "Fashion"},
                ]
            }
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_trending_categories(
                ad_account=mock_ad_account, catalog_id="cat1"
            )
        assert len(result["categories"]) == 2
        assert result["categories"][0]["name"] == "Electronics"
        mock_gateway.get.assert_called_once_with(
            "/catalog/insights/category/trending/",
            params={"bc_id": "adv_123", "catalog_id": "cat1"},
        )


class TestGetProductDiagnostics:
    @pytest.mark.asyncio
    async def test_get_product_diagnostics_default_pagination(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "products": [
                    {"product_id": "p1", "issue": "missing_image"},
                ]
            }
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_product_diagnostics(
                ad_account=mock_ad_account, catalog_id="cat1"
            )
        assert len(result["products"]) == 1
        assert result["products"][0]["issue"] == "missing_image"
        mock_gateway.get.assert_called_once_with(
            "/catalog/diagnostics/product/get/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_get_product_diagnostics_custom_pagination(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"products": []}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_product_diagnostics(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                page=3,
                page_size=50,
            )
        assert result["products"] == []
        mock_gateway.get.assert_called_once_with(
            "/catalog/diagnostics/product/get/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "page": "3",
                "page_size": "50",
            },
        )


class TestGetEventSourceDiagnostics:
    @pytest.mark.asyncio
    async def test_get_event_source_diagnostics(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "event_sources": [
                    {"event_source_id": "es1", "status": "ACTIVE"},
                ]
            }
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_event_source_diagnostics(
                ad_account=mock_ad_account, catalog_id="cat1"
            )
        assert len(result["event_sources"]) == 1
        assert result["event_sources"][0]["status"] == "ACTIVE"
        mock_gateway.get.assert_called_once_with(
            "/catalog/diagnostics/event_source/get/",
            params={"bc_id": "adv_123", "catalog_id": "cat1"},
        )


class TestBindEventSource:
    @pytest.mark.asyncio
    async def test_bind_event_source(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.bind_event_source(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                event_source_id="es1",
            )
        assert result["success"] is True
        mock_gateway.post.assert_called_once_with(
            "/catalog/event_source/bind/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "event_source_id": "es1",
            },
        )


class TestUnbindEventSource:
    @pytest.mark.asyncio
    async def test_unbind_event_source(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.unbind_event_source(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                event_source_id="es1",
            )
        assert result == {}
        mock_gateway.post.assert_called_once_with(
            "/catalog/event_source/unbind/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "event_source_id": "es1",
            },
        )
