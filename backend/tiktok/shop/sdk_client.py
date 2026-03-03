"""TikTok Shop SDK sidecar client.

Proxies TikTok Shop API calls through the Node.js SDK sidecar service,
which handles HMAC-SHA256 signing using the official TikTok SDK.

Provides two interfaces:
1. Direct: client.call(domain, version, operation, params, body)
2. Gateway-compatible: client.request(method, path, params, json_body)
   Drop-in replacement for TikTokShopClient within PlatformGateway.
"""

import logging
from typing import Any

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


class TikTokShopSDKError(Exception):
    """Error from the TikTok Shop SDK sidecar."""

    def __init__(self, code: str, message: str, details: Any = None) -> None:
        self.code = code
        self.details = details
        super().__init__(f"{code}: {message}")


class TikTokShopSDKClient:
    """Client that proxies TikTok Shop API calls through the Node.js SDK sidecar."""

    def __init__(
        self,
        access_token: str,
        shop_cipher: str | None = None,
        sdk_base_url: str | None = None,
        sidecar_auth_token: str | None = None,
    ) -> None:
        self._access_token = access_token
        self._shop_cipher = shop_cipher
        self._base_url = sdk_base_url or settings.tiktok_shop_sdk_url
        self._sidecar_auth_token = sidecar_auth_token or settings.sidecar_auth_token
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=60.0,
            headers={"x-sidecar-auth": self._sidecar_auth_token},
        )

    async def __aenter__(self) -> "TikTokShopSDKClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def call(
        self,
        domain: str,
        version: str,
        operation: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call an SDK operation via the sidecar signing proxy."""
        # Build the TikTok API path from domain/version/operation convention
        # e.g. ("product", "V202502", "ProductsSearchPost") -> "/product/202502/products/search"
        version_num = version.lstrip("V")
        path = f"/{domain}/{version_num}/{self._operation_to_path(operation)}"

        return await self._proxy_request(
            method="POST",
            path=path,
            query_params=params,
            body=body,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Gateway-compatible interface matching TikTokShopClient.request()."""
        return await self._proxy_request(
            method=method,
            path=path,
            query_params=params,
            body=json_body,
        )

    async def get(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("POST", path, params=params, json_body=json_body)

    async def close(self) -> None:
        await self._client.aclose()

    async def _proxy_request(
        self,
        method: str,
        path: str,
        query_params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a request through the sidecar signing proxy."""
        payload: dict[str, Any] = {
            "method": method,
            "path": path,
            "access_token": self._access_token,
        }
        if self._shop_cipher:
            payload["shop_cipher"] = self._shop_cipher
        if query_params:
            payload["query_params"] = query_params
        if body:
            payload["body"] = body

        try:
            response = await self._client.post("/api/shop/proxy", json=payload)
        except httpx.HTTPError as exc:
            raise TikTokShopSDKError(
                code="SIDECAR_UNREACHABLE",
                message=f"Failed to reach SDK sidecar: {exc}",
            ) from exc

        try:
            data = response.json()
        except Exception as exc:
            raise TikTokShopSDKError(
                code="SIDECAR_INVALID_RESPONSE",
                message=f"Sidecar returned non-JSON response (HTTP {response.status_code})",
            ) from exc

        if response.status_code == 401:
            raise TikTokShopSDKError(
                code="SIDECAR_AUTH_FAILED",
                message="Sidecar authentication failed — check SIDECAR_AUTH_TOKEN",
            )

        if not data.get("success"):
            error = data.get("error", {})
            raise TikTokShopSDKError(
                code=error.get("code", "UNKNOWN"),
                message=error.get("message", "Unknown error"),
                details=error.get("details"),
            )

        return data.get("data", {})

    @staticmethod
    def _operation_to_path(operation: str) -> str:
        """Convert SDK operation name to URL path segment.

        e.g. "ProductsSearchPost" -> "products/search"
        Strips trailing HTTP method suffix (Get/Post/Put/Delete).
        """
        # Strip trailing method name
        for suffix in ("Post", "Get", "Put", "Delete", "Patch"):
            if operation.endswith(suffix):
                operation = operation[: -len(suffix)]
                break

        # Convert PascalCase to lowercase with / separators
        result: list[str] = []
        current: list[str] = []
        for char in operation:
            if char.isupper() and current:
                result.append("".join(current).lower())
                current = [char]
            else:
                current.append(char)
        if current:
            result.append("".join(current).lower())

        return "/".join(result)
