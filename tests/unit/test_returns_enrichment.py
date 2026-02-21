import uuid

import pytest
from unittest.mock import AsyncMock, patch

from backend.modules.commerce.services.return_service import ReturnService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestCreateReturn:
    @pytest.mark.asyncio
    async def test_create_return_calls_post_and_returns_data(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"return_id": "ret-001", "status": "PENDING"}
        }

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.create_return(
                shop_id,
                order_id="order-123",
                return_type="RETURN_AND_REFUND",
                reason="Item damaged",
            )

            assert result == {"return_id": "ret-001", "status": "PENDING"}
            mock_gateway.post.assert_called_once_with(
                "/return_refund/202309/returns",
                json_body={
                    "order_id": "order-123",
                    "return_type": "RETURN_AND_REFUND",
                    "reason": "Item damaged",
                },
            )

    @pytest.mark.asyncio
    async def test_create_return_empty_data(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            result = await service.create_return(
                uuid.uuid4(),
                order_id="order-456",
                return_type="REFUND_ONLY",
                reason="Wrong item",
            )

            assert result == {}


class TestSearchReturns:
    @pytest.mark.asyncio
    async def test_search_returns_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {
                "returns": [
                    {"return_id": "ret-001", "status": "PENDING"},
                    {"return_id": "ret-002", "status": "APPROVED"},
                ]
            }
        }

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.search_returns(shop_id)

            assert len(result) == 2
            assert result[0]["return_id"] == "ret-001"
            mock_gateway.post.assert_called_once_with(
                "/return_refund/202309/returns/search",
                json_body={},
            )

    @pytest.mark.asyncio
    async def test_search_returns_with_filters(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"returns": [{"return_id": "ret-003"}]}
        }

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            result = await service.search_returns(
                uuid.uuid4(), status="PENDING", order_id="order-789"
            )

            assert len(result) == 1
            mock_gateway.post.assert_called_once_with(
                "/return_refund/202309/returns/search",
                json_body={"status": "PENDING", "order_id": "order-789"},
            )

    @pytest.mark.asyncio
    async def test_search_returns_empty(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"returns": []}}

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            result = await service.search_returns(uuid.uuid4())

            assert result == []


class TestGetReturnRecords:
    @pytest.mark.asyncio
    async def test_get_return_records_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "records": [
                    {"record_id": "rec-001", "action": "CREATE"},
                    {"record_id": "rec-002", "action": "APPROVE"},
                ]
            }
        }

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.get_return_records(shop_id, "ret-001")

            assert len(result) == 2
            assert result[0]["record_id"] == "rec-001"
            mock_gateway.get.assert_called_once_with(
                "/return_refund/202309/returns/ret-001/records"
            )


class TestGetRejectReasons:
    @pytest.mark.asyncio
    async def test_get_reject_reasons_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        reasons = [
            {"reason_id": "r1", "reason_text": "Item not received"},
            {"reason_id": "r2", "reason_text": "Incorrect item"},
        ]
        mock_gateway.get.return_value = {"data": {"reasons": reasons}}

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.get_reject_reasons(shop_id)

            assert len(result) == 2
            assert result[0]["reason_id"] == "r1"
            mock_gateway.get.assert_called_once_with(
                "/return_refund/202309/reject_reasons"
            )


class TestCalculateRefund:
    @pytest.mark.asyncio
    async def test_calculate_refund_returns_data(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {
                "refund_amount": "29.99",
                "currency": "USD",
            }
        }
        items = [
            {"item_id": "item-1", "quantity": 1},
            {"item_id": "item-2", "quantity": 2},
        ]

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.calculate_refund(
                shop_id, order_id="order-123", items=items
            )

            assert result["refund_amount"] == "29.99"
            assert result["currency"] == "USD"
            mock_gateway.post.assert_called_once_with(
                "/return_refund/202309/refund/calculate",
                json_body={"order_id": "order-123", "items": items},
            )

    @pytest.mark.asyncio
    async def test_calculate_refund_empty_items(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"refund_amount": "0.00"}}

        with patch.object(
            ReturnService, "_get_gateway", return_value=mock_gateway
        ):
            service = ReturnService(mock_session)
            result = await service.calculate_refund(
                uuid.uuid4(), order_id="order-456", items=[]
            )

            assert result["refund_amount"] == "0.00"


class TestGetGateway:
    @pytest.mark.asyncio
    async def test_get_gateway_raises_when_shop_not_found(
        self,
        mock_session: AsyncMock,
    ) -> None:
        with patch(
            "backend.modules.commerce.services.return_service.ShopService"
        ) as mock_shop_svc_cls:
            mock_shop_svc = AsyncMock()
            mock_shop_svc.get_shop.return_value = None
            mock_shop_svc_cls.return_value = mock_shop_svc

            service = ReturnService(mock_session)
            shop_id = uuid.uuid4()

            with pytest.raises(ValueError, match=f"Shop {shop_id} not found"):
                await service._get_gateway(shop_id)
