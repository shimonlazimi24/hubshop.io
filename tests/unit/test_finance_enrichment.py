import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.commerce.services.finance_service import FinanceService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestGetWithdrawals:
    @pytest.mark.asyncio
    async def test_get_withdrawals_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "withdrawals": [
                    {"withdrawal_id": "wd-001", "amount": "100.00"},
                    {"withdrawal_id": "wd-002", "amount": "250.00"},
                ]
            }
        }

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.get_withdrawals(shop_id)

            assert len(result) == 2
            assert result[0]["withdrawal_id"] == "wd-001"
            assert result[1]["amount"] == "250.00"
            mock_gateway.get.assert_called_once_with("/finance/202309/withdrawals")

    @pytest.mark.asyncio
    async def test_get_withdrawals_empty(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"withdrawals": []}}

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_withdrawals(uuid.uuid4())

            assert result == []


class TestGetTransactionsByOrder:
    @pytest.mark.asyncio
    async def test_get_transactions_by_order_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "transactions": [
                    {"transaction_id": "txn-001", "amount": "49.99"},
                    {"transaction_id": "txn-002", "amount": "10.00"},
                ]
            }
        }

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.get_transactions_by_order(shop_id, "order-123")

            assert len(result) == 2
            assert result[0]["transaction_id"] == "txn-001"
            mock_gateway.get.assert_called_once_with(
                "/finance/202501/orders/order-123/transactions"
            )

    @pytest.mark.asyncio
    async def test_get_transactions_by_order_empty(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"transactions": []}}

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_transactions_by_order(uuid.uuid4(), "order-456")

            assert result == []


class TestGetTransactionsByStatement:
    @pytest.mark.asyncio
    async def test_get_transactions_by_statement_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "transactions": [
                    {"transaction_id": "txn-100", "type": "SALE"},
                    {"transaction_id": "txn-101", "type": "REFUND"},
                ]
            }
        }

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.get_transactions_by_statement(shop_id, "stmt-789")

            assert len(result) == 2
            assert result[1]["type"] == "REFUND"
            mock_gateway.get.assert_called_once_with(
                "/finance/202501/statements/stmt-789/transactions"
            )

    @pytest.mark.asyncio
    async def test_get_transactions_by_statement_empty(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"transactions": []}}

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_transactions_by_statement(
                uuid.uuid4(), "stmt-000"
            )

            assert result == []


class TestGetUnsettledTransactions:
    @pytest.mark.asyncio
    async def test_get_unsettled_transactions_returns_list(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "transactions": [
                    {"transaction_id": "txn-u1", "status": "UNSETTLED"},
                    {"transaction_id": "txn-u2", "status": "UNSETTLED"},
                    {"transaction_id": "txn-u3", "status": "UNSETTLED"},
                ]
            }
        }

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            shop_id = uuid.uuid4()
            result = await service.get_unsettled_transactions(shop_id)

            assert len(result) == 3
            assert result[0]["transaction_id"] == "txn-u1"
            mock_gateway.get.assert_called_once_with(
                "/finance/202507/transactions/unsettled"
            )

    @pytest.mark.asyncio
    async def test_get_unsettled_transactions_empty(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"transactions": []}}

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_unsettled_transactions(uuid.uuid4())

            assert result == []


class TestGetGateway:
    @pytest.mark.asyncio
    async def test_get_gateway_raises_when_shop_not_found(
        self,
        mock_session: AsyncMock,
    ) -> None:
        with patch(
            "backend.modules.commerce.services.finance_service.ShopService"
        ) as mock_shop_svc_cls:
            mock_shop_svc = AsyncMock()
            mock_shop_svc.get_shop.return_value = None
            mock_shop_svc_cls.return_value = mock_shop_svc

            service = FinanceService(mock_session)
            shop_id = uuid.uuid4()

            with pytest.raises(ValueError, match=f"Shop {shop_id} not found"):
                await service._get_gateway(shop_id)

    @pytest.mark.asyncio
    async def test_get_gateway_calls_build_gateway_for_shop(
        self,
        mock_session: AsyncMock,
    ) -> None:
        mock_shop = AsyncMock()
        mock_gw = AsyncMock()

        with patch(
            "backend.modules.commerce.services.finance_service.ShopService"
        ) as mock_shop_svc_cls:
            mock_shop_svc = AsyncMock()
            mock_shop_svc.get_shop.return_value = mock_shop
            mock_shop_svc.build_gateway_for_shop.return_value = mock_gw
            mock_shop_svc_cls.return_value = mock_shop_svc

            service = FinanceService(mock_session)
            shop_id = uuid.uuid4()
            result = await service._get_gateway(shop_id)

            assert result is mock_gw
            mock_shop_svc.get_shop.assert_called_once_with(shop_id)
            mock_shop_svc.build_gateway_for_shop.assert_called_once_with(mock_shop)


class TestMissingDataKey:
    """Test resilience when API returns unexpected response shapes."""

    @pytest.mark.asyncio
    async def test_get_withdrawals_missing_data_key(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {}

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_withdrawals(uuid.uuid4())

            assert result == []

    @pytest.mark.asyncio
    async def test_get_transactions_by_order_missing_transactions_key(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {}}

        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_transactions_by_order(uuid.uuid4(), "order-999")

            assert result == []
