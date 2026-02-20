"""Tests for SymphonyService — smart creative, text recommendations, CTA, smart fix, fatigue."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.symphony_service import SymphonyService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_account_service(
    sample_ad_account: SimpleNamespace, mock_gateway: AsyncMock
):
    with patch(
        "backend.modules.advertising.services.symphony_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestGetSmartCreativeMaterials:
    @pytest.mark.asyncio
    async def test_get_smart_creative_materials(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "materials": [
                    {"material_id": "m1", "type": "image"},
                ]
            }
        }

        service = SymphonyService(mock_session)
        result = await service.get_smart_creative_materials(
            sample_ad_account.workspace_id, sample_ad_account, "ad_123"
        )

        assert len(result["materials"]) == 1
        assert result["materials"][0]["material_id"] == "m1"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["ad_id"] == "ad_123"


class TestCreateSmartCreativeAd:
    @pytest.mark.asyncio
    async def test_create_smart_creative_ad(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"ad_id": "ad_new", "status": "created"}
        }

        ad_config = {
            "ad_name": "Symphony Smart Ad",
            "creative_type": "SMART_CREATIVE",
            "landing_page_url": "https://example.com",
        }

        service = SymphonyService(mock_session)
        result = await service.create_smart_creative_ad(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_config=ad_config,
        )

        assert result["ad_id"] == "ad_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["ad_name"] == "Symphony Smart Ad"
        assert call_body["creative_type"] == "SMART_CREATIVE"


class TestUpdateSmartCreativeMaterials:
    @pytest.mark.asyncio
    async def test_update_smart_creative_materials(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"ad_id": "ad_123"}}

        materials = [
            {"material_id": "m1", "url": "https://example.com/img1.jpg"},
            {"material_id": "m2", "url": "https://example.com/img2.jpg"},
        ]

        service = SymphonyService(mock_session)
        result = await service.update_smart_creative_materials(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_id="ad_123",
            materials=materials,
        )

        assert result["ad_id"] == "ad_123"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["ad_id"] == "ad_123"
        assert len(call_body["materials"]) == 2


class TestRecommendSmartText:
    @pytest.mark.asyncio
    async def test_recommend_smart_text(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "recommendations": [
                    {"text": "Shop now for the best deals!", "score": 0.95},
                ]
            }
        }

        service = SymphonyService(mock_session)
        result = await service.recommend_smart_text(
            sample_ad_account.workspace_id,
            sample_ad_account,
            "Buy our product",
        )

        assert len(result["recommendations"]) == 1
        assert result["recommendations"][0]["score"] == 0.95
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["ad_text"] == "Buy our product"


class TestRecommendCta:
    @pytest.mark.asyncio
    async def test_recommend_cta(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "ctas": [
                    {"cta_text": "Shop Now", "cta_id": "SHOP_NOW"},
                    {"cta_text": "Learn More", "cta_id": "LEARN_MORE"},
                ]
            }
        }

        service = SymphonyService(mock_session)
        result = await service.recommend_cta(
            sample_ad_account.workspace_id,
            sample_ad_account,
            "CONVERSIONS",
        )

        assert len(result["ctas"]) == 2
        assert result["ctas"][0]["cta_id"] == "SHOP_NOW"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["objective"] == "CONVERSIONS"


class TestCreateSmartFix:
    @pytest.mark.asyncio
    async def test_create_smart_fix(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"task_id": "task_abc", "status": "processing"}
        }

        service = SymphonyService(mock_session)
        result = await service.create_smart_fix(
            sample_ad_account.workspace_id,
            sample_ad_account,
            creative_id="cr_456",
        )

        assert result["task_id"] == "task_abc"
        assert result["status"] == "processing"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["creative_id"] == "cr_456"


class TestGetSmartFixResult:
    @pytest.mark.asyncio
    async def test_get_smart_fix_result(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "task_id": "task_abc",
                "status": "completed",
                "fixed_creative_id": "cr_789",
            }
        }

        service = SymphonyService(mock_session)
        result = await service.get_smart_fix_result(
            sample_ad_account.workspace_id,
            sample_ad_account,
            "task_abc",
        )

        assert result["status"] == "completed"
        assert result["fixed_creative_id"] == "cr_789"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["task_id"] == "task_abc"


class TestDetectFatigue:
    @pytest.mark.asyncio
    async def test_detect_fatigue(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "results": [
                    {"ad_id": "ad_1", "fatigue_score": 0.8, "is_fatigued": True},
                    {"ad_id": "ad_2", "fatigue_score": 0.2, "is_fatigued": False},
                ]
            }
        }

        service = SymphonyService(mock_session)
        result = await service.detect_fatigue(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ["ad_1", "ad_2"],
        )

        assert len(result["results"]) == 2
        assert result["results"][0]["is_fatigued"] is True
        assert result["results"][1]["is_fatigued"] is False
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["ad_ids"] == ["ad_1", "ad_2"]
