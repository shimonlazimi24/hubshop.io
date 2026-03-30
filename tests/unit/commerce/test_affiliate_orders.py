"""Tests for E3: Affiliate order tracking."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.commerce.services.affiliate_service import AffiliateService


class TestListAffiliateOrders:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_list_affiliate_orders_basic(self, mock_session: AsyncMock) -> None:
        """Should return paginated affiliate orders for workspace."""
        from backend.db.models.affiliate import AffiliateOrder

        workspace_id = uuid.uuid4()
        order = MagicMock(spec=AffiliateOrder)
        order.id = uuid.uuid4()
        order.workspace_id = workspace_id

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [order]

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_affiliate_orders(workspace_id)

        assert result.total == 1
        assert result.page == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_list_affiliate_orders_with_shop_filter(
        self, mock_session: AsyncMock
    ) -> None:
        """Should filter by shop_id when provided."""
        workspace_id = uuid.uuid4()
        shop_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_affiliate_orders(workspace_id, shop_id=shop_id)

        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_affiliate_orders_with_creator_filter(
        self, mock_session: AsyncMock
    ) -> None:
        """Should filter by creator_id when provided."""
        workspace_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_affiliate_orders(
            workspace_id, creator_id="creator_abc"
        )

        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_affiliate_orders_pagination(
        self, mock_session: AsyncMock
    ) -> None:
        """Should respect page and page_size parameters."""
        workspace_id = uuid.uuid4()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 100
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AffiliateService(mock_session)
        result = await service.list_affiliate_orders(workspace_id, page=5, page_size=10)

        assert result.total == 100
        assert result.page == 5
        assert result.page_size == 10
        assert result.total_pages == 10


class TestSyncAffiliateOrders:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_sync_affiliate_orders_creates_new(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should fetch orders from API and upsert."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "orders": [
                    {
                        "order_id": "aff_order_1",
                        "creator_id": "cr_1",
                        "collab_type": "OPEN",
                        "product_id": "prod_1",
                        "order_amount": "99.99",
                        "commission_rate": "10",
                        "commission_amount": "9.99",
                    },
                    {
                        "order_id": "aff_order_2",
                        "creator_id": "cr_2",
                        "collab_type": "TARGET",
                        "product_id": "prod_2",
                        "order_amount": "49.99",
                        "commission_rate": "15",
                        "commission_amount": "7.49",
                    },
                ]
            }
        }

        # Mock existing order lookup returns None (new)
        find_result = MagicMock()
        find_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=find_result)

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            count = await service.sync_affiliate_orders(mock_shop)

        assert count == 2
        assert mock_session.add.call_count == 2

    @pytest.mark.asyncio
    async def test_sync_affiliate_orders_empty_response(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should return 0 when API returns no orders."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"orders": []}}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            count = await service.sync_affiliate_orders(mock_shop)

        assert count == 0


class TestAffiliateOrderModel:
    def test_affiliate_order_model_exists(self) -> None:
        """AffiliateOrder model should be importable."""
        from backend.db.models.affiliate import AffiliateOrder

        assert AffiliateOrder.__tablename__ == "affiliate_orders"

    def test_affiliate_order_in_init(self) -> None:
        """AffiliateOrder should be exported from models __init__."""
        from backend.db.models import AffiliateOrder

        assert AffiliateOrder is not None
