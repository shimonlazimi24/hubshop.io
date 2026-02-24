from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.tiktok.research.client import TikTokResearchClient


@pytest.mark.unit
class TestTikTokResearchClient:
    def test_init(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        assert client._client_key == "key"
        assert client._client_secret == "secret"
        assert client._access_token is None

    def test_base_url(self) -> None:
        assert (
            TikTokResearchClient.BASE_URL == "https://open.tiktokapis.com/v2/research"
        )

    def test_token_url(self) -> None:
        assert (
            TikTokResearchClient.TOKEN_URL
            == "https://open.tiktokapis.com/v2/oauth/token/"
        )

    @pytest.mark.asyncio
    async def test_ensure_token_fetches_when_missing(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"access_token": "new_token"}}
        mock_resp.raise_for_status = MagicMock()
        with patch.object(
            client._http, "post", new_callable=AsyncMock, return_value=mock_resp
        ):
            token = await client._ensure_token()
            assert token == "new_token"
            assert client._access_token == "new_token"

    @pytest.mark.asyncio
    async def test_ensure_token_reuses_cached(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        client._access_token = "cached_token"
        token = await client._ensure_token()
        assert token == "cached_token"

    @pytest.mark.asyncio
    async def test_query_videos(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        client._access_token = "fake_token"
        with patch.object(client._http, "request", new_callable=AsyncMock) as mock:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"data": {"videos": [{"id": "123"}]}}
            mock_resp.raise_for_status = MagicMock()
            mock.return_value = mock_resp
            result = await client.query_videos(
                hashtag_name="test", start_date="20260101", end_date="20260201"
            )
            assert result["data"]["videos"][0]["id"] == "123"

    @pytest.mark.asyncio
    async def test_query_user_info(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        client._access_token = "fake_token"
        with patch.object(client._http, "request", new_callable=AsyncMock) as mock:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"data": {"display_name": "testuser"}}
            mock_resp.raise_for_status = MagicMock()
            mock.return_value = mock_resp
            result = await client.query_user_info(username="testuser")
            assert result["data"]["display_name"] == "testuser"

    @pytest.mark.asyncio
    async def test_query_video_comments(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        client._access_token = "fake_token"
        with patch.object(client._http, "request", new_callable=AsyncMock) as mock:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"data": {"comments": [{"text": "nice"}]}}
            mock_resp.raise_for_status = MagicMock()
            mock.return_value = mock_resp
            result = await client.query_video_comments(video_id="456")
            assert result["data"]["comments"][0]["text"] == "nice"

    @pytest.mark.asyncio
    async def test_query_user_followers(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        client._access_token = "fake_token"
        with patch.object(client._http, "request", new_callable=AsyncMock) as mock:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"data": {"followers": []}}
            mock_resp.raise_for_status = MagicMock()
            mock.return_value = mock_resp
            result = await client.query_user_followers(username="user1")
            assert result["data"]["followers"] == []

    @pytest.mark.asyncio
    async def test_get_method(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        client._access_token = "fake_token"
        with patch.object(client._http, "request", new_callable=AsyncMock) as mock:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"data": {}}
            mock_resp.raise_for_status = MagicMock()
            mock.return_value = mock_resp
            await client.get("/some/path", params={"key": "val"})
            mock.assert_called_once()
            args = mock.call_args
            assert args[0][0] == "GET"

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        client = TikTokResearchClient(client_key="key", client_secret="secret")
        with patch.object(client._http, "aclose", new_callable=AsyncMock) as mock_close:
            await client.close()
            mock_close.assert_called_once()
