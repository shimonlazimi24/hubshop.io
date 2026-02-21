import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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


class TestListProductSets:
    @pytest.mark.asyncio
    async def test_returns_product_sets(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"product_set_id": "ps1", "name": "Set 1"},
                    {"product_set_id": "ps2", "name": "Set 2"},
                ]
            }
        }
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.list_product_sets(
                ad_account=mock_ad_account, catalog_id="cat_001"
            )
            assert len(result["list"]) == 2
            assert result["list"][0]["product_set_id"] == "ps1"
            mock_gateway.get.assert_called_once_with(
                "/catalog/product_set/get/",
                params={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "page": "1",
                    "page_size": "20",
                },
            )

    @pytest.mark.asyncio
    async def test_custom_pagination(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            await service.list_product_sets(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                page=3,
                page_size=50,
            )
            mock_gateway.get.assert_called_once_with(
                "/catalog/product_set/get/",
                params={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "page": "3",
                    "page_size": "50",
                },
            )


class TestGetProductSetProducts:
    @pytest.mark.asyncio
    async def test_returns_products(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"product_id": "p1", "title": "Product 1"},
                ]
            }
        }
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.get_product_set_products(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                product_set_id="ps1",
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["product_id"] == "p1"
            mock_gateway.get.assert_called_once_with(
                "/catalog/product_set/product/get/",
                params={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_id": "ps1",
                    "page": "1",
                    "page_size": "20",
                },
            )


class TestCreateProductSetByConditions:
    @pytest.mark.asyncio
    async def test_creates_product_set(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        conditions = [
            {"field": "price", "operator": "GREATER_THAN", "value": "10"}
        ]
        mock_gateway.post.return_value = {
            "data": {"product_set_id": "ps_new"}
        }
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.create_product_set_by_conditions(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                name="Expensive Items",
                conditions=conditions,
            )
            assert result["product_set_id"] == "ps_new"
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/condition/create/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_name": "Expensive Items",
                    "conditions": conditions,
                },
            )


class TestCreateProductSetByFile:
    @pytest.mark.asyncio
    async def test_creates_product_set_from_file(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"product_set_id": "ps_file"}
        }
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.create_product_set_by_file(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                name="File Set",
                file_url="https://example.com/products.csv",
            )
            assert result["product_set_id"] == "ps_file"
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/file/create/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_name": "File Set",
                    "file_url": "https://example.com/products.csv",
                },
            )


class TestUpdateProductSet:
    @pytest.mark.asyncio
    async def test_update_name_only(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.update_product_set(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                product_set_id="ps1",
                name="Updated Name",
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/update/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_id": "ps1",
                    "product_set_name": "Updated Name",
                },
            )

    @pytest.mark.asyncio
    async def test_update_conditions_only(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        new_conditions = [
            {"field": "category", "operator": "EQUALS", "value": "shoes"}
        ]
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.update_product_set(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                product_set_id="ps1",
                conditions=new_conditions,
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/update/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_id": "ps1",
                    "conditions": new_conditions,
                },
            )

    @pytest.mark.asyncio
    async def test_update_both_name_and_conditions(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        conditions = [{"field": "brand", "operator": "EQUALS", "value": "Nike"}]
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.update_product_set(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                product_set_id="ps1",
                name="Nike Products",
                conditions=conditions,
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/update/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_id": "ps1",
                    "product_set_name": "Nike Products",
                    "conditions": conditions,
                },
            )


class TestDeleteProductSets:
    @pytest.mark.asyncio
    async def test_delete_single(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.delete_product_sets(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                product_set_ids=["ps1"],
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/delete/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_ids": ["ps1"],
                },
            )

    @pytest.mark.asyncio
    async def test_delete_multiple(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            CatalogService, "_get_gateway", return_value=mock_gateway
        ):
            service = CatalogService(mock_session)
            result = await service.delete_product_sets(
                ad_account=mock_ad_account,
                catalog_id="cat_001",
                product_set_ids=["ps1", "ps2", "ps3"],
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/catalog/product_set/delete/",
                json_body={
                    "bc_id": "adv_123",
                    "catalog_id": "cat_001",
                    "product_set_ids": ["ps1", "ps2", "ps3"],
                },
            )
