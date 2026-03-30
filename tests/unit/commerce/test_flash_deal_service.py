"""Tests for flash deal creation with validation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.promotion_service import PromotionService


class TestCreateFlashDeal:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(id=uuid.uuid4(), workspace_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_flash_deal_validates_duration(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        service = PromotionService(mock_session)
        with pytest.raises(ValueError, match="72 hours"):
            await service.create_flash_deal(
                sample_shop.workspace_id,
                sample_shop,
                title="Bad Deal",
                product_ids=["prod_1"],
                countdown_duration_hours=73,
                price_rules=[],
            )

    @pytest.mark.asyncio
    async def test_create_flash_deal_validates_min_duration(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        service = PromotionService(mock_session)
        with pytest.raises(ValueError, match="at least 1 hour"):
            await service.create_flash_deal(
                sample_shop.workspace_id,
                sample_shop,
                title="Too Short",
                product_ids=["prod_1"],
                countdown_duration_hours=0,
                price_rules=[],
            )

    @pytest.mark.asyncio
    async def test_create_flash_deal_calls_api(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        service = PromotionService(mock_session)

        with patch(
            "backend.modules.commerce.services.promotion_service.ShopService"
        ) as MockShopService:
            mock_shop_svc = AsyncMock()
            gateway = AsyncMock()
            gateway.post.return_value = {"data": {"activity_id": "act_flash_001"}}
            mock_shop_svc.build_gateway_for_shop.return_value = gateway
            MockShopService.return_value = mock_shop_svc

            result = await service.create_flash_deal(
                sample_shop.workspace_id,
                sample_shop,
                title="Summer Flash",
                product_ids=["prod_1"],
                countdown_duration_hours=48,
                max_quantity=100,
                price_rules=[
                    {
                        "sku_id": "sku_1",
                        "original_price": "29.99",
                        "discount_price": "19.99",
                    }
                ],
            )

        assert result.promotion_type == "FLASH_DEAL"
        assert result.countdown_duration_hours == 48
        assert result.max_quantity == 100
        gateway.post.assert_called_once()
