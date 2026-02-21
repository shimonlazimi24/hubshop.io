import uuid

import pytest
from unittest.mock import AsyncMock, patch

from backend.modules.commerce.services.fulfillment_service import FulfillmentService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestSplitOrder:
    @pytest.mark.asyncio
    async def test_split_order_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"packages": [{"id": "pkg1"}, {"id": "pkg2"}]}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.split_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                groups=[["sku1", "sku2"], ["sku3"]],
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/fulfillment/202309/orders/split"

    @pytest.mark.asyncio
    async def test_split_order_sends_correct_body(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"packages": []}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.split_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                groups=[["sku1"], ["sku2"]],
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["order_id"] == "order123"
            assert body["groups"] == [["sku1"], ["sku2"]]

    @pytest.mark.asyncio
    async def test_split_order_returns_packages(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"packages": [{"id": "pkg1"}, {"id": "pkg2"}]}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.split_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                groups=[["sku1"], ["sku2"]],
            )
            assert len(result) == 2
            assert result[0]["id"] == "pkg1"

    @pytest.mark.asyncio
    async def test_split_order_empty_response(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.split_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                groups=[],
            )
            assert result == []


class TestBatchShipPackages:
    @pytest.mark.asyncio
    async def test_batch_ship_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"results": [{"package_id": "pkg1", "status": "shipped"}]}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.batch_ship_packages(
                shop_id=uuid.uuid4(),
                packages=[{"id": "pkg1", "tracking_number": "TN1"}],
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/fulfillment/202309/packages/batch_ship"

    @pytest.mark.asyncio
    async def test_batch_ship_sends_correct_body(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        packages_input = [
            {"id": "pkg1", "tracking_number": "TN1"},
            {"id": "pkg2", "tracking_number": "TN2"},
        ]
        mock_gateway.post.return_value = {"data": {"results": []}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.batch_ship_packages(
                shop_id=uuid.uuid4(),
                packages=packages_input,
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["packages"] == packages_input

    @pytest.mark.asyncio
    async def test_batch_ship_returns_results(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {
                "results": [
                    {"package_id": "pkg1", "status": "shipped"},
                    {"package_id": "pkg2", "status": "shipped"},
                ]
            }
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.batch_ship_packages(
                shop_id=uuid.uuid4(),
                packages=[{"id": "pkg1"}, {"id": "pkg2"}],
            )
            assert len(result) == 2
            assert result[0]["status"] == "shipped"


class TestSearchPackages:
    @pytest.mark.asyncio
    async def test_search_packages_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"packages": [{"id": "pkg1"}]}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.search_packages(shop_id=uuid.uuid4())
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/fulfillment/202309/packages/search"

    @pytest.mark.asyncio
    async def test_search_packages_returns_packages(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"packages": [{"id": "pkg1"}, {"id": "pkg2"}]}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.search_packages(shop_id=uuid.uuid4())
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_packages_empty_response(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.search_packages(shop_id=uuid.uuid4())
            assert result == []


class TestGetShippingDocument:
    @pytest.mark.asyncio
    async def test_get_shipping_document_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"document_url": "https://example.com/label.pdf"}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.get_shipping_document(
                shop_id=uuid.uuid4(),
                package_id="pkg123",
            )
            endpoint = mock_gateway.get.call_args[0][0]
            assert (
                endpoint
                == "/fulfillment/202309/packages/pkg123/shipping_document"
            )

    @pytest.mark.asyncio
    async def test_get_shipping_document_sends_correct_params(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.get_shipping_document(
                shop_id=uuid.uuid4(),
                package_id="pkg123",
                document_type="PACKING_LIST",
            )
            params = mock_gateway.get.call_args[1].get("params", {})
            assert params["document_type"] == "PACKING_LIST"

    @pytest.mark.asyncio
    async def test_get_shipping_document_default_type(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.get_shipping_document(
                shop_id=uuid.uuid4(),
                package_id="pkg123",
            )
            params = mock_gateway.get.call_args[1].get("params", {})
            assert params["document_type"] == "SHIPPING_LABEL"

    @pytest.mark.asyncio
    async def test_get_shipping_document_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"document_url": "https://example.com/label.pdf"}
        }
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.get_shipping_document(
                shop_id=uuid.uuid4(),
                package_id="pkg123",
            )
            assert result["document_url"] == "https://example.com/label.pdf"


class TestUpdateShippingInfo:
    @pytest.mark.asyncio
    async def test_update_shipping_info_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "updated"}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.update_shipping_info(
                shop_id=uuid.uuid4(),
                order_id="order123",
                tracking_number="TN999",
                shipping_provider_id="fedex",
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert (
                endpoint
                == "/fulfillment/202309/packages/shipping_info/update"
            )

    @pytest.mark.asyncio
    async def test_update_shipping_info_sends_correct_body(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "updated"}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            await service.update_shipping_info(
                shop_id=uuid.uuid4(),
                order_id="order123",
                tracking_number="TN999",
                shipping_provider_id="fedex",
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["order_id"] == "order123"
            assert body["tracking_number"] == "TN999"
            assert body["shipping_provider_id"] == "fedex"

    @pytest.mark.asyncio
    async def test_update_shipping_info_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "updated"}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.update_shipping_info(
                shop_id=uuid.uuid4(),
                order_id="order123",
                tracking_number="TN999",
                shipping_provider_id="fedex",
            )
            assert result == {"status": "updated"}

    @pytest.mark.asyncio
    async def test_update_shipping_info_empty_response(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            FulfillmentService, "_get_gateway", return_value=mock_gateway
        ):
            service = FulfillmentService(mock_session)
            result = await service.update_shipping_info(
                shop_id=uuid.uuid4(),
                order_id="order123",
                tracking_number="TN999",
                shipping_provider_id="ups",
            )
            assert result == {}
