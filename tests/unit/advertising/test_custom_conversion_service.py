"""Tests for CustomConversionService — list, detail, create, update, delete conversions."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.custom_conversion_service import (
    CustomConversionService,
)


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
        "backend.modules.advertising.services.custom_conversion_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestListConversions:
    @pytest.mark.asyncio
    async def test_list_conversions(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"custom_conversion_id": "cc1", "name": "Purchase"},
                ]
            }
        }

        service = CustomConversionService(mock_session)
        result = await service.list_conversions(
            sample_ad_account.workspace_id,
            sample_ad_account,
            pixel_id="px1",
        )

        assert len(result["list"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["pixel_id"] == "px1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetConversionDetail:
    @pytest.mark.asyncio
    async def test_get_conversion_detail(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "custom_conversion_id": "cc1",
                "name": "Purchase",
                "pixel_id": "px1",
            }
        }

        service = CustomConversionService(mock_session)
        result = await service.get_conversion_detail(
            sample_ad_account.workspace_id,
            sample_ad_account,
            custom_conversion_id="cc1",
        )

        assert result["custom_conversion_id"] == "cc1"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["custom_conversion_id"] == "cc1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestCreateConversion:
    @pytest.mark.asyncio
    async def test_create_conversion(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"custom_conversion_id": "cc_new", "name": "Add to Cart"}
        }

        conversion_config = {
            "name": "Add to Cart",
            "pixel_id": "px1",
            "rules": [{"type": "URL", "value": "/cart"}],
        }

        service = CustomConversionService(mock_session)
        result = await service.create_conversion(
            sample_ad_account.workspace_id,
            sample_ad_account,
            conversion_config=conversion_config,
        )

        assert result["custom_conversion_id"] == "cc_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["name"] == "Add to Cart"
        assert call_body["pixel_id"] == "px1"


class TestUpdateConversion:
    @pytest.mark.asyncio
    async def test_update_conversion(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"custom_conversion_id": "cc1"}
        }

        service = CustomConversionService(mock_session)
        result = await service.update_conversion(
            sample_ad_account.workspace_id,
            sample_ad_account,
            custom_conversion_id="cc1",
            updates={"name": "Updated Conversion"},
        )

        assert result["custom_conversion_id"] == "cc1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["custom_conversion_id"] == "cc1"
        assert call_body["name"] == "Updated Conversion"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestDeleteConversion:
    @pytest.mark.asyncio
    async def test_delete_conversion(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        service = CustomConversionService(mock_session)
        result = await service.delete_conversion(
            sample_ad_account.workspace_id,
            sample_ad_account,
            custom_conversion_id="cc1",
        )

        assert result == {}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["custom_conversion_id"] == "cc1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
