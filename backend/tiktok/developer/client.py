from typing import Any

import httpx


class TikTokDeveloperClient:
    """TikTok Developer API client with Bearer token auth."""

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
