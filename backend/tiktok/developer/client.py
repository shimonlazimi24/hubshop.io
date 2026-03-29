import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class TokenExpiredError(Exception):
    """Raised when the Developer API access token has expired."""


class TikTokDeveloperClient:
    """TikTok Developer API client with Bearer token auth.

    Detects 401 responses and raises TokenExpiredError so callers
    can trigger token refresh via the token vault.
    """

    BASE_URL = "https://open.tiktokapis.com/v2"

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    def update_token(self, access_token: str) -> None:
        """Update the access token after a refresh."""
        self._access_token = access_token
        self._client.headers["Authorization"] = f"Bearer {access_token}"

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a Bearer-authenticated request to TikTok Developer API."""
        response = await self._client.request(
            method,
            path,
            params=params,
            json=json_body,
        )
        if response.status_code == 401:
            logger.warning("Developer API token expired (401) on %s %s", method, path)
            raise TokenExpiredError(
                f"Access token expired for Developer API ({method} {path})"
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
