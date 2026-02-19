from typing import Any

import httpx


class TikTokMarketingClient:
    """TikTok Marketing API client with custom Access-Token header."""

    BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
            headers={
                "Access-Token": access_token,
                "Content-Type": "application/json",
            },
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to TikTok Marketing API."""
        response = await self._client.request(
            method,
            path,
            params=params,
            json=json_body,
        )
        response.raise_for_status()
        return response.json()

    async def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
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
