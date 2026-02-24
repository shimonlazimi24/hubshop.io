import hashlib
import hmac
import time
from typing import Any

import httpx

from backend.config import settings


class TikTokShopClient:
    """TikTok Shop API client with HMAC-SHA256 request signing."""

    BASE_URL = "https://open-api.tiktokglobalshop.com"

    def __init__(self, access_token: str, shop_cipher: str | None = None) -> None:
        self._access_token = access_token
        self._shop_cipher = shop_cipher
        self._app_key = settings.tiktok_shop_app_key
        self._app_secret = settings.tiktok_shop_app_secret
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        )

    def _generate_signature(
        self,
        path: str,
        params: dict[str, str],
        body: str = "",
    ) -> str:
        """Generate HMAC-SHA256 signature per TikTok Shop API spec.

        Sign string = app_secret + path + sorted(param_key+param_value) + body + app_secret
        """
        # Exclude 'sign' and 'access_token' from signature base
        excluded = {"sign", "access_token"}
        sorted_params = "".join(
            f"{k}{v}" for k, v in sorted(params.items()) if k not in excluded
        )
        base_string = f"{self._app_secret}{path}{sorted_params}{body}{self._app_secret}"
        return hmac.new(
            self._app_secret.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _build_common_params(self) -> dict[str, str]:
        return {
            "app_key": self._app_key,
            "timestamp": str(int(time.time())),
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a signed request to TikTok Shop API."""
        all_params = self._build_common_params()
        if self._shop_cipher:
            all_params["shop_cipher"] = self._shop_cipher
        if params:
            all_params.update(params)

        import json as json_module

        body_str = (
            json_module.dumps(json_body, separators=(",", ":")) if json_body else ""
        )
        all_params["sign"] = self._generate_signature(path, all_params, body_str)
        all_params["access_token"] = self._access_token

        headers = {
            "Content-Type": "application/json",
            "x-tts-access-token": self._access_token,
        }

        response = await self._client.request(
            method,
            path,
            params=all_params,
            content=body_str if body_str else None,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get(
        self, path: str, params: dict[str, str] | None = None
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
