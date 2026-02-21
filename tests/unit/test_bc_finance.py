import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.modules.advertising.services.business_center_service import (
    BusinessCenterService,
)


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


class TestGetBcBalance:
    @pytest.mark.asyncio
    async def test_returns_balance(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"balance": 5000.00, "currency": "USD"}
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.get_bc_balance(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert result["balance"] == 5000.00
            assert result["currency"] == "USD"
            mock_gateway.get.assert_called_once_with(
                "/bc/payment/balance/get/",
                params={"bc_id": "bc_001"},
            )


class TestProcessPayment:
    @pytest.mark.asyncio
    async def test_grant_payment(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"transaction_id": "txn_001", "status": "SUCCESS"}
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.process_payment(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                advertiser_id="adv_456",
                transfer_type="GRANT",
                amount=1000.50,
            )
            assert result["transaction_id"] == "txn_001"
            assert result["status"] == "SUCCESS"
            mock_gateway.post.assert_called_once_with(
                "/bc/payment/process/",
                json_body={
                    "bc_id": "bc_001",
                    "advertiser_id": "adv_456",
                    "transfer_type": "GRANT",
                    "amount": 1000.50,
                },
            )

    @pytest.mark.asyncio
    async def test_reclaim_payment(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"transaction_id": "txn_002", "status": "SUCCESS"}
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.process_payment(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                advertiser_id="adv_456",
                transfer_type="RECLAIM",
                amount=250.00,
            )
            assert result["transaction_id"] == "txn_002"
            mock_gateway.post.assert_called_once_with(
                "/bc/payment/process/",
                json_body={
                    "bc_id": "bc_001",
                    "advertiser_id": "adv_456",
                    "transfer_type": "RECLAIM",
                    "amount": 250.00,
                },
            )


class TestListTransactions:
    @pytest.mark.asyncio
    async def test_returns_transactions_default_pagination(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"transaction_id": "txn_001", "amount": 100.00},
                    {"transaction_id": "txn_002", "amount": 200.00},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_transactions(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 2
            mock_gateway.get.assert_called_once_with(
                "/bc/payment/transaction/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )

    @pytest.mark.asyncio
    async def test_returns_transactions_custom_pagination(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            await service.list_transactions(
                ad_account=mock_ad_account, bc_id="bc_001", page=3, page_size=50
            )
            mock_gateway.get.assert_called_once_with(
                "/bc/payment/transaction/get/",
                params={"bc_id": "bc_001", "page": "3", "page_size": "50"},
            )


class TestListBillingGroups:
    @pytest.mark.asyncio
    async def test_returns_billing_groups(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"billing_group_id": "bg_001", "billing_group_name": "Group A"},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_billing_groups(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["billing_group_name"] == "Group A"
            mock_gateway.get.assert_called_once_with(
                "/bc/billing_group/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )


class TestCreateBillingGroup:
    @pytest.mark.asyncio
    async def test_create_without_advertiser_ids(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"billing_group_id": "bg_new_001"}
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.create_billing_group(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                billing_group_name="New Group",
            )
            assert result["billing_group_id"] == "bg_new_001"
            mock_gateway.post.assert_called_once_with(
                "/bc/billing_group/create/",
                json_body={
                    "bc_id": "bc_001",
                    "billing_group_name": "New Group",
                },
            )

    @pytest.mark.asyncio
    async def test_create_with_advertiser_ids(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"billing_group_id": "bg_new_002"}
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.create_billing_group(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                billing_group_name="Group With Advertisers",
                advertiser_ids=["adv_001", "adv_002"],
            )
            assert result["billing_group_id"] == "bg_new_002"
            mock_gateway.post.assert_called_once_with(
                "/bc/billing_group/create/",
                json_body={
                    "bc_id": "bc_001",
                    "billing_group_name": "Group With Advertisers",
                    "advertiser_ids": ["adv_001", "adv_002"],
                },
            )


class TestListInvoices:
    @pytest.mark.asyncio
    async def test_returns_invoices(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"invoice_id": "inv_001", "total": 999.99},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_invoices(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["invoice_id"] == "inv_001"
            mock_gateway.get.assert_called_once_with(
                "/bc/invoice/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )


class TestGetCostRecords:
    @pytest.mark.asyncio
    async def test_returns_cost_records(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"cost_id": "cost_001", "amount": 150.00},
                    {"cost_id": "cost_002", "amount": 300.00},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.get_cost_records(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 2
            mock_gateway.get.assert_called_once_with(
                "/bc/payment/cost/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )
