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


class TestListFeeds:
    @pytest.mark.asyncio
    async def test_list_feeds_default_pagination(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"feed_id": "f1", "feed_name": "Daily Feed"},
                    {"feed_id": "f2", "feed_name": "Weekly Feed"},
                ]
            }
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.list_feeds(
                ad_account=mock_ad_account, catalog_id="cat1"
            )
        assert len(result["list"]) == 2
        assert result["list"][0]["feed_id"] == "f1"
        mock_gateway.get.assert_called_once_with(
            "/catalog/feed/get/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_list_feeds_custom_pagination(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.list_feeds(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                page=3,
                page_size=10,
            )
        assert result["list"] == []
        mock_gateway.get.assert_called_once_with(
            "/catalog/feed/get/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "page": "3",
                "page_size": "10",
            },
        )


class TestCreateFeed:
    @pytest.mark.asyncio
    async def test_create_feed_minimal(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"feed_id": "f_new"}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.create_feed(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_name="My Feed",
                feed_url="https://example.com/feed.csv",
            )
        assert result["feed_id"] == "f_new"
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/create/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_name": "My Feed",
                "feed_url": "https://example.com/feed.csv",
                "auto_update": True,
            },
        )

    @pytest.mark.asyncio
    async def test_create_feed_with_schedule(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        schedule = {"interval": "DAILY", "time": "03:00"}
        mock_gateway.post.return_value = {"data": {"feed_id": "f_sched"}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.create_feed(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_name="Scheduled Feed",
                feed_url="https://example.com/feed.csv",
                auto_update=True,
                schedule=schedule,
            )
        assert result["feed_id"] == "f_sched"
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/create/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_name": "Scheduled Feed",
                "feed_url": "https://example.com/feed.csv",
                "auto_update": True,
                "schedule": schedule,
            },
        )

    @pytest.mark.asyncio
    async def test_create_feed_auto_update_false(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"feed_id": "f_manual"}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.create_feed(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_name="Manual Feed",
                feed_url="https://example.com/manual.csv",
                auto_update=False,
            )
        assert result["feed_id"] == "f_manual"
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/create/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_name": "Manual Feed",
                "feed_url": "https://example.com/manual.csv",
                "auto_update": False,
            },
        )


class TestUpdateFeed:
    @pytest.mark.asyncio
    async def test_update_feed_name(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.update_feed(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_id="f1",
                feed_name="Renamed Feed",
            )
        assert result == {}
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/update/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_id": "f1",
                "feed_name": "Renamed Feed",
            },
        )

    @pytest.mark.asyncio
    async def test_update_feed_url(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.update_feed(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_id="f1",
                feed_url="https://example.com/new-feed.csv",
            )
        assert result == {}
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/update/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_id": "f1",
                "feed_url": "https://example.com/new-feed.csv",
            },
        )


class TestDeleteFeed:
    @pytest.mark.asyncio
    async def test_delete_feed(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.delete_feed(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_id="f1",
            )
        assert result == {}
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/delete/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_id": "f1",
            },
        )


class TestGetFeedLog:
    @pytest.mark.asyncio
    async def test_get_feed_log(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [{"log_id": "log1", "status": "SUCCESS", "items_synced": 150}]
            }
        }
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.get_feed_log(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_id="f1",
            )
        assert len(result["list"]) == 1
        assert result["list"][0]["status"] == "SUCCESS"
        mock_gateway.get.assert_called_once_with(
            "/catalog/feed/log/",
            params={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_id": "f1",
                "page": "1",
                "page_size": "20",
            },
        )


class TestUpdateFeedSchedule:
    @pytest.mark.asyncio
    async def test_update_feed_schedule(
        self,
        service: CatalogService,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        schedule = {"interval": "WEEKLY", "time": "06:00"}
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(service, "_get_gateway", return_value=mock_gateway):
            result = await service.update_feed_schedule(
                ad_account=mock_ad_account,
                catalog_id="cat1",
                feed_id="f1",
                schedule=schedule,
            )
        assert result == {}
        mock_gateway.post.assert_called_once_with(
            "/catalog/feed/schedule/update/",
            json_body={
                "bc_id": "adv_123",
                "catalog_id": "cat1",
                "feed_id": "f1",
                "schedule": schedule,
            },
        )
