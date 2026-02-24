import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.commerce.services.order_service import OrderService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestCancelOrder:
    @pytest.mark.asyncio
    async def test_cancel_order_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"cancellation_id": "c1"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.cancel_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                cancel_reason="out_of_stock",
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/return_refund/202309/cancellations"

    @pytest.mark.asyncio
    async def test_cancel_order_sends_correct_body(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"cancellation_id": "c1"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.cancel_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                cancel_reason="out_of_stock",
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["order_id"] == "order123"
            assert body["cancel_reason"] == "out_of_stock"

    @pytest.mark.asyncio
    async def test_cancel_order_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"cancellation_id": "c1"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.cancel_order(
                shop_id=uuid.uuid4(),
                order_id="order123",
                cancel_reason="out_of_stock",
            )
            assert result == {"cancellation_id": "c1"}


class TestApproveCancellation:
    @pytest.mark.asyncio
    async def test_approve_cancellation_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "approved"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.approve_cancellation(
                shop_id=uuid.uuid4(), order_id="order123"
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/return_refund/202309/cancellations/order123/approve"

    @pytest.mark.asyncio
    async def test_approve_cancellation_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "approved"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.approve_cancellation(
                shop_id=uuid.uuid4(), order_id="order123"
            )
            assert result == {"status": "approved"}


class TestRejectCancellation:
    @pytest.mark.asyncio
    async def test_reject_cancellation_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "rejected"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.reject_cancellation(
                shop_id=uuid.uuid4(),
                order_id="order456",
                reject_reason="already_shipped",
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/return_refund/202309/cancellations/order456/reject"

    @pytest.mark.asyncio
    async def test_reject_cancellation_sends_reason(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "rejected"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.reject_cancellation(
                shop_id=uuid.uuid4(),
                order_id="order456",
                reject_reason="already_shipped",
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["reject_reason"] == "already_shipped"

    @pytest.mark.asyncio
    async def test_reject_cancellation_without_reason(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"status": "rejected"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.reject_cancellation(
                shop_id=uuid.uuid4(),
                order_id="order456",
            )
            body = mock_gateway.post.call_args[1].get("json_body")
            assert body is None


class TestSearchCancellations:
    @pytest.mark.asyncio
    async def test_search_cancellations_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"cancellations": [{"id": "c1"}, {"id": "c2"}]}
        }
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.search_cancellations(shop_id=uuid.uuid4())
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/return_refund/202309/cancellations/search"

    @pytest.mark.asyncio
    async def test_search_cancellations_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"cancellations": [{"id": "c1"}, {"id": "c2"}]}
        }
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.search_cancellations(shop_id=uuid.uuid4())
            assert len(result) == 2
            assert result[0]["id"] == "c1"

    @pytest.mark.asyncio
    async def test_search_cancellations_empty_response(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.search_cancellations(shop_id=uuid.uuid4())
            assert result == []


class TestGetPriceDetail:
    @pytest.mark.asyncio
    async def test_get_price_detail_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"subtotal": "100.00", "shipping": "5.00"}
        }
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.get_price_detail(shop_id=uuid.uuid4(), order_id="order789")
            endpoint = mock_gateway.get.call_args[0][0]
            assert endpoint == "/order/202407/orders/order789/price_detail"

    @pytest.mark.asyncio
    async def test_get_price_detail_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"subtotal": "100.00", "shipping": "5.00"}
        }
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.get_price_detail(
                shop_id=uuid.uuid4(), order_id="order789"
            )
            assert result["subtotal"] == "100.00"
            assert result["shipping"] == "5.00"
