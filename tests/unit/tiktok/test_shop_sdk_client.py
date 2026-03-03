"""Tests for TikTokShopSDKClient — the sidecar proxy client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from backend.tiktok.shop.sdk_client import TikTokShopSDKClient, TikTokShopSDKError

SIDECAR_AUTH_TOKEN = "test-sidecar-token"


@pytest.fixture
def mock_httpx_response():
    """Factory for creating mock httpx responses."""

    def _make(status_code: int, json_data: dict) -> httpx.Response:
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data
        response.raise_for_status = MagicMock()
        if status_code >= 400:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "error", request=MagicMock(), response=response
            )
        return response

    return _make


class TestSDKClientCall:
    """Test the direct .call() interface."""

    @pytest.mark.asyncio
    async def test_successful_call(self, mock_httpx_response: object) -> None:
        mock_resp = mock_httpx_response(
            200,
            {
                "success": True,
                "data": {"products": [{"id": "123", "title": "Test Product"}]},
                "request_id": "req-001",
            },
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            result = await client.call(
                "product",
                "V202502",
                "ProductsSearchPost",
                params={"pageSize": 50},
                body={"status": "LIVE"},
            )

            assert result == {"products": [{"id": "123", "title": "Test Product"}]}

            # Verify the correct URL was called
            call_args = mock_instance.post.call_args
            assert call_args[0][0] == "/api/shop/proxy"

            # Verify request body structure
            payload = call_args[1]["json"]
            assert payload["access_token"] == "test_token"
            assert payload["method"] == "POST"
            assert payload["path"] == "/product/202502/products/search"

            await client.close()

    @pytest.mark.asyncio
    async def test_call_with_shop_cipher(self, mock_httpx_response: object) -> None:
        mock_resp = mock_httpx_response(
            200,
            {"success": True, "data": {}, "request_id": "req-002"},
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                shop_cipher="TTP_abc123",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            await client.call("product", "V202502", "ProductsSearchPost")

            payload = mock_instance.post.call_args[1]["json"]
            assert payload["shop_cipher"] == "TTP_abc123"
            await client.close()

    @pytest.mark.asyncio
    async def test_call_error_response(self, mock_httpx_response: object) -> None:
        mock_resp = mock_httpx_response(
            200,
            {
                "success": False,
                "error": {
                    "code": "INVALID_OPERATION",
                    "message": "Operation not found",
                },
                "request_id": "req-003",
            },
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            with pytest.raises(TikTokShopSDKError, match="INVALID_OPERATION"):
                await client.call("product", "V9999", "FakeOp")
            await client.close()


class TestSDKClientGatewayInterface:
    """Test the gateway-compatible .request()/.get()/.post() interface."""

    @pytest.mark.asyncio
    async def test_request_translates_path(
        self, mock_httpx_response: object
    ) -> None:
        mock_resp = mock_httpx_response(
            200,
            {
                "success": True,
                "data": {"code": 0, "data": {"shops": []}},
                "request_id": "req-004",
            },
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            result = await client.request(
                "GET", "/authorization/202309/shops"
            )

            assert "data" in result

            # Verify it went through the proxy endpoint
            call_args = mock_instance.post.call_args
            assert call_args[0][0] == "/api/shop/proxy"
            payload = call_args[1]["json"]
            assert payload["method"] == "GET"
            assert payload["path"] == "/authorization/202309/shops"
            await client.close()

    @pytest.mark.asyncio
    async def test_post_with_json_body(self, mock_httpx_response: object) -> None:
        mock_resp = mock_httpx_response(
            200,
            {
                "success": True,
                "data": {"data": {"products": []}},
                "request_id": "req-005",
            },
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            result = await client.post(
                "/product/202309/products/search",
                json_body={"page_size": 50},
            )

            payload = mock_instance.post.call_args[1]["json"]
            assert payload["body"] == {"page_size": 50}
            assert payload["path"] == "/product/202309/products/search"
            await client.close()

    @pytest.mark.asyncio
    async def test_get_shorthand(self, mock_httpx_response: object) -> None:
        mock_resp = mock_httpx_response(
            200,
            {
                "success": True,
                "data": {"categories": []},
                "request_id": "req-006",
            },
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            await client.get("/product/202309/categories")

            payload = mock_instance.post.call_args[1]["json"]
            assert payload["method"] == "GET"
            await client.close()


class TestSDKClientConnectionHandling:
    """Test connection lifecycle."""

    @pytest.mark.asyncio
    async def test_close_calls_aclose(self) -> None:
        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            await client.close()
            mock_instance.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_default_sdk_url_from_settings(self) -> None:
        with patch("backend.tiktok.shop.sdk_client.settings") as mock_settings:
            mock_settings.tiktok_shop_sdk_url = "http://custom:9000"
            mock_settings.sidecar_auth_token = "settings-token"

            with patch(
                "backend.tiktok.shop.sdk_client.httpx.AsyncClient"
            ) as MockClient:
                mock_instance = AsyncMock()
                MockClient.return_value = mock_instance

                client = TikTokShopSDKClient(access_token="test_token")

                MockClient.assert_called_once()
                call_kwargs = MockClient.call_args[1]
                assert call_kwargs["base_url"] == "http://custom:9000"
                assert call_kwargs["headers"] == {"x-sidecar-auth": "settings-token"}

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            async with TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            ) as client:
                assert client is not None
            mock_instance.aclose.assert_called_once()


class TestSDKClientErrorHandling:
    """Test error handling for sidecar communication failures."""

    @pytest.mark.asyncio
    async def test_sidecar_unreachable(self) -> None:
        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.ConnectError("Connection refused")
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            with pytest.raises(TikTokShopSDKError, match="SIDECAR_UNREACHABLE"):
                await client.request("GET", "/authorization/202309/shops")
            await client.close()

    @pytest.mark.asyncio
    async def test_sidecar_auth_failure(self, mock_httpx_response: object) -> None:
        mock_resp = mock_httpx_response(
            401,
            {"error": "Unauthorized"},
        )

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token="wrong-token",
            )
            with pytest.raises(TikTokShopSDKError, match="SIDECAR_AUTH_FAILED"):
                await client.request("GET", "/authorization/202309/shops")
            await client.close()

    @pytest.mark.asyncio
    async def test_sidecar_invalid_json_response(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("Invalid JSON")

        with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_resp
            mock_instance.aclose = AsyncMock()
            MockClient.return_value = mock_instance

            client = TikTokShopSDKClient(
                access_token="test_token",
                sdk_base_url="http://localhost:4000",
                sidecar_auth_token=SIDECAR_AUTH_TOKEN,
            )
            with pytest.raises(TikTokShopSDKError, match="SIDECAR_INVALID_RESPONSE"):
                await client.request("GET", "/authorization/202309/shops")
            await client.close()
