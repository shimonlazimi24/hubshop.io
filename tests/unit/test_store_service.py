import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.modules.advertising.services.store_service import StoreService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestListStores:
    @pytest.mark.asyncio
    async def test_list_stores_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "stores": [{"store_id": "s1"}, {"store_id": "s2"}],
                "total": 2,
            }
        }
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.list_stores(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert result["stores"] == [{"store_id": "s1"}, {"store_id": "s2"}]
        assert result["total"] == 2
        mock_gateway.get.assert_called_once_with(
            "/store/get/",
            params={
                "advertiser_id": "adv1",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_list_stores_empty_result(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.list_stores(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert result == {}


class TestGetStoreProducts:
    @pytest.mark.asyncio
    async def test_get_store_products_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "products": [{"product_id": "p1"}, {"product_id": "p2"}],
                "total": 2,
            }
        }
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.get_store_products(
                ad_account=MagicMock(advertiser_id="adv1"),
                store_id="store_123",
            )
        assert len(result["products"]) == 2
        mock_gateway.get.assert_called_once_with(
            "/store/product/get/",
            params={
                "advertiser_id": "adv1",
                "store_id": "store_123",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_get_store_products_custom_pagination(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"products": [{"product_id": "p5"}], "total": 1}
        }
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.get_store_products(
                ad_account=MagicMock(advertiser_id="adv1"),
                store_id="store_123",
                page=3,
                page_size=10,
            )
        assert result["products"] == [{"product_id": "p5"}]
        mock_gateway.get.assert_called_once_with(
            "/store/product/get/",
            params={
                "advertiser_id": "adv1",
                "store_id": "store_123",
                "page": "3",
                "page_size": "10",
            },
        )


class TestGetShowcaseIdentities:
    @pytest.mark.asyncio
    async def test_get_showcase_identities_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "identities": [
                    {"identity_id": "id1", "display_name": "Shop A"},
                    {"identity_id": "id2", "display_name": "Shop B"},
                ]
            }
        }
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.get_showcase_identities(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert len(result["identities"]) == 2
        assert result["identities"][0]["display_name"] == "Shop A"
        mock_gateway.get.assert_called_once_with(
            "/showcase/identity/get/",
            params={"advertiser_id": "adv1"},
        )

    @pytest.mark.asyncio
    async def test_get_showcase_identities_empty_result(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.get_showcase_identities(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert result == {}


class TestGetShowcaseProducts:
    @pytest.mark.asyncio
    async def test_get_showcase_products_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "products": [{"product_id": "sp1"}, {"product_id": "sp2"}],
                "total": 2,
            }
        }
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.get_showcase_products(
                ad_account=MagicMock(advertiser_id="adv1"),
                identity_id="identity_456",
            )
        assert len(result["products"]) == 2
        mock_gateway.get.assert_called_once_with(
            "/showcase/product/get/",
            params={
                "advertiser_id": "adv1",
                "identity_id": "identity_456",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_get_showcase_products_custom_pagination(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"products": [{"product_id": "sp10"}], "total": 1}
        }
        with patch.object(
            StoreService, "_get_gateway", return_value=mock_gateway
        ):
            service = StoreService(mock_session)
            result = await service.get_showcase_products(
                ad_account=MagicMock(advertiser_id="adv1"),
                identity_id="identity_456",
                page=2,
                page_size=5,
            )
        assert result["products"] == [{"product_id": "sp10"}]
        mock_gateway.get.assert_called_once_with(
            "/showcase/product/get/",
            params={
                "advertiser_id": "adv1",
                "identity_id": "identity_456",
                "page": "2",
                "page_size": "5",
            },
        )
