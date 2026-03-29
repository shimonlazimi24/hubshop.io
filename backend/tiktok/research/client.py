"""TikTok Research API client.

Uses client credentials OAuth for authentication.
Base URL: https://open.tiktokapis.com/v2/research/
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class TikTokResearchClient:
    """Async client for TikTok Research API.

    Uses client credentials OAuth for authentication.
    Base URL: https://open.tiktokapis.com/v2/research/
    """

    BASE_URL = "https://open.tiktokapis.com/v2/research"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

    def __init__(self, client_key: str, client_secret: str) -> None:
        self._client_key = client_key
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._http = httpx.AsyncClient(timeout=30.0)

    async def _ensure_token(self) -> str:
        """Get or refresh access token via client credentials."""
        if self._access_token:
            return self._access_token
        resp = await self._http.post(
            self.TOKEN_URL,
            json={
                "client_key": self._client_key,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data.get("data", {}).get("access_token", "")
        return self._access_token

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Research API."""
        token = await self._ensure_token()
        response = await self._http.request(
            method,
            f"{self.BASE_URL}{path}",
            params=params,
            json=json_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    async def get(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """HTTP GET helper."""
        return await self.request("GET", path, params=params)

    async def post(
        self, path: str, json_body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """HTTP POST helper."""
        return await self.request("POST", path, json_body=json_body)

    async def query_videos(
        self,
        *,
        hashtag_name: str | None = None,
        keyword: str | None = None,
        username: str | None = None,
        region_code: str | None = None,
        start_date: str,
        end_date: str,
        max_count: int = 100,
    ) -> dict[str, Any]:
        """Search public videos by criteria."""
        conditions: dict[str, list[dict[str, Any]]] = {"and": []}
        if hashtag_name:
            conditions["and"].append(
                {
                    "field_name": "hashtag_name",
                    "operation": "EQ",
                    "field_values": [hashtag_name],
                }
            )
        if keyword:
            conditions["and"].append(
                {
                    "field_name": "keyword",
                    "operation": "EQ",
                    "field_values": [keyword],
                }
            )
        if username:
            conditions["and"].append(
                {
                    "field_name": "username",
                    "operation": "EQ",
                    "field_values": [username],
                }
            )
        if region_code:
            conditions["and"].append(
                {
                    "field_name": "region_code",
                    "operation": "IN",
                    "field_values": [region_code],
                }
            )

        return await self.post(
            "/video/query/",
            json_body={
                "query": conditions,
                "start_date": start_date,
                "end_date": end_date,
                "max_count": max_count,
                "fields": (
                    "id,create_time,username,video_description,"
                    "like_count,comment_count,share_count,view_count,"
                    "hashtag_names,music_id"
                ),
            },
        )

    async def query_user_info(self, username: str) -> dict[str, Any]:
        """Get public user profile information."""
        return await self.post(
            "/user/info/",
            json_body={
                "username": username,
                "fields": (
                    "display_name,follower_count,following_count,"
                    "likes_count,video_count,bio_description,avatar_url"
                ),
            },
        )

    async def query_video_comments(
        self, video_id: str, max_count: int = 100
    ) -> dict[str, Any]:
        """List comments on a public video."""
        return await self.post(
            "/video/comment/list/",
            json_body={
                "video_id": int(video_id),
                "max_count": max_count,
            },
        )

    async def query_user_followers(
        self, username: str, max_count: int = 100
    ) -> dict[str, Any]:
        """List followers of a public user.

        NOTE: The /research/user/followers/ endpoint does NOT exist in the
        TikTok Research API.  This method is retained for interface
        compatibility but will always raise ``NotImplementedError``.
        """
        raise NotImplementedError(
            "TikTok Research API does not provide a /research/user/followers/ endpoint"
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.aclose()
