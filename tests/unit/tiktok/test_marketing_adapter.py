"""Tests for TikTok Marketing SDK adapter."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.tiktok.marketing.client import TikTokMarketingClient


@pytest.mark.unit
class TestTikTokMarketingClient:
    def test_init(self) -> None:
        client = TikTokMarketingClient(access_token="test_token")
        assert client._access_token == "test_token"

    @pytest.mark.asyncio
    async def test_get_backward_compat(self) -> None:
        client = TikTokMarketingClient(access_token="test_token")
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"code": 0, "data": {}}
            result = await client.get("/campaign/get/", params={"page": "1"})
            assert result["code"] == 0

    @pytest.mark.asyncio
    async def test_post_backward_compat(self) -> None:
        client = TikTokMarketingClient(access_token="test_token")
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"code": 0, "data": {"campaign_id": "123"}}
            result = await client.post("/campaign/create/", json_body={"name": "test"})
            assert result["data"]["campaign_id"] == "123"

    def test_has_sdk_config_attribute(self) -> None:
        client = TikTokMarketingClient(access_token="test_token")
        assert hasattr(client, "sdk_config")

    def test_has_sdk_property(self) -> None:
        client = TikTokMarketingClient(access_token="test_token")
        assert hasattr(client, "sdk")
        # SDK may or may not be available depending on install
        _ = client.sdk

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        client = TikTokMarketingClient(access_token="test_token")
        await client.close()  # Should not raise
