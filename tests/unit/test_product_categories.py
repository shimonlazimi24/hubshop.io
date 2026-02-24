from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestGetCategories:
    @pytest.mark.asyncio
    async def test_get_categories_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "categories": [
                    {
                        "id": "1",
                        "parent_id": "0",
                        "local_name": "Electronics",
                        "is_leaf": False,
                    },
                    {
                        "id": "2",
                        "parent_id": "1",
                        "local_name": "Phones",
                        "is_leaf": True,
                    },
                ]
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_categories(shop_id=MagicMock())
            assert len(result) == 2
            assert result[0]["local_name"] == "Electronics"
            assert result[1]["local_name"] == "Phones"
            mock_gateway.get.assert_called_once_with("/product/202309/categories")

    @pytest.mark.asyncio
    async def test_get_categories_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"categories": []}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_categories(shop_id=MagicMock())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_categories_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_categories(shop_id=MagicMock())
            assert result == []


class TestRecommendCategories:
    @pytest.mark.asyncio
    async def test_recommend_categories(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"categories": [{"id": "100", "local_name": "Shoes"}]}
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.recommend_categories(
                shop_id=MagicMock(), product_title="Nike Air Max"
            )
            assert len(result) == 1
            assert result[0]["id"] == "100"
            mock_gateway.post.assert_called_once_with(
                "/product/202309/categories/recommend",
                json_body={"product_title": "Nike Air Max"},
            )

    @pytest.mark.asyncio
    async def test_recommend_categories_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"categories": []}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.recommend_categories(
                shop_id=MagicMock(), product_title="Unknown product xyz"
            )
            assert result == []


class TestGetCategoryRules:
    @pytest.mark.asyncio
    async def test_get_category_rules(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "category_rules": [{"property": "size_chart", "is_required": True}]
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_category_rules(
                shop_id=MagicMock(), category_id="100"
            )
            assert len(result) == 1
            assert result[0]["property"] == "size_chart"
            assert result[0]["is_required"] is True
            mock_gateway.get.assert_called_once_with(
                "/product/202309/categories/100/rules"
            )

    @pytest.mark.asyncio
    async def test_get_category_rules_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"category_rules": []}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_category_rules(
                shop_id=MagicMock(), category_id="999"
            )
            assert result == []


class TestGetAttributes:
    @pytest.mark.asyncio
    async def test_get_attributes(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"attributes": [{"id": "a1", "name": "Color", "is_required": True}]}
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_attributes(
                shop_id=MagicMock(), category_id="100"
            )
            assert len(result) == 1
            assert result[0]["name"] == "Color"
            assert result[0]["is_required"] is True
            mock_gateway.get.assert_called_once_with(
                "/product/202309/categories/100/attributes"
            )

    @pytest.mark.asyncio
    async def test_get_attributes_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"attributes": []}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_attributes(
                shop_id=MagicMock(), category_id="999"
            )
            assert result == []


class TestGetGateway:
    @pytest.mark.asyncio
    async def test_get_gateway_shop_not_found(self, mock_session: AsyncMock) -> None:
        with patch(
            "backend.modules.commerce.services.product_service.ShopService"
        ) as mock_shop_service_cls:
            mock_shop_service = AsyncMock()
            mock_shop_service.get_shop.return_value = None
            mock_shop_service_cls.return_value = mock_shop_service

            service = ProductService(mock_session)
            with pytest.raises(ValueError, match="not found"):
                await service._get_gateway(MagicMock())

    @pytest.mark.asyncio
    async def test_get_gateway_returns_gateway(self, mock_session: AsyncMock) -> None:
        with patch(
            "backend.modules.commerce.services.product_service.ShopService"
        ) as mock_shop_service_cls:
            mock_shop = MagicMock()
            mock_gateway = AsyncMock()
            mock_shop_service = AsyncMock()
            mock_shop_service.get_shop.return_value = mock_shop
            mock_shop_service.build_gateway_for_shop.return_value = mock_gateway
            mock_shop_service_cls.return_value = mock_shop_service

            service = ProductService(mock_session)
            result = await service._get_gateway(MagicMock())
            assert result is mock_gateway
