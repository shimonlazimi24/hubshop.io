import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.creative_service import CreativeService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_ad_account() -> MagicMock:
    account = MagicMock()
    account.advertiser_id = "adv_123"
    return account


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


class TestUploadVideo:
    @pytest.mark.asyncio
    async def test_upload_video_by_url(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"video_id": "v_001"}}
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.upload_video(
                workspace_id,
                mock_ad_account,
                video_url="https://example.com/video.mp4",
            )
            assert result["video_id"] == "v_001"
            mock_gateway.post.assert_called_once_with(
                "/file/video/ad/upload/",
                json_body={
                    "advertiser_id": "adv_123",
                    "upload_type": "UPLOAD_BY_URL",
                    "video_url": "https://example.com/video.mp4",
                },
            )

    @pytest.mark.asyncio
    async def test_upload_video_with_name(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"video_id": "v_002"}}
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.upload_video(
                workspace_id,
                mock_ad_account,
                video_url="https://example.com/video.mp4",
                video_name="my_video.mp4",
            )
            assert result["video_id"] == "v_002"
            mock_gateway.post.assert_called_once_with(
                "/file/video/ad/upload/",
                json_body={
                    "advertiser_id": "adv_123",
                    "upload_type": "UPLOAD_BY_URL",
                    "video_url": "https://example.com/video.mp4",
                    "file_name": "my_video.mp4",
                },
            )


class TestGetVideoInfo:
    @pytest.mark.asyncio
    async def test_get_video_info(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"video_id": "v_001", "duration": 30},
                    {"video_id": "v_002", "duration": 15},
                ]
            }
        }
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.get_video_info(
                workspace_id,
                mock_ad_account,
                video_ids=["v_001", "v_002"],
            )
            assert len(result["list"]) == 2
            mock_gateway.get.assert_called_once_with(
                "/file/video/ad/info/",
                params={
                    "advertiser_id": "adv_123",
                    "video_ids": json.dumps(["v_001", "v_002"]),
                },
            )


class TestUploadImage:
    @pytest.mark.asyncio
    async def test_upload_image_by_url(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"image_id": "img_001"}}
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.upload_image(
                workspace_id,
                mock_ad_account,
                image_url="https://example.com/image.png",
            )
            assert result["image_id"] == "img_001"
            mock_gateway.post.assert_called_once_with(
                "/file/image/ad/upload/",
                json_body={
                    "advertiser_id": "adv_123",
                    "upload_type": "UPLOAD_BY_URL",
                    "image_url": "https://example.com/image.png",
                },
            )

    @pytest.mark.asyncio
    async def test_upload_image_with_name(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"image_id": "img_002"}}
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.upload_image(
                workspace_id,
                mock_ad_account,
                image_url="https://example.com/image.png",
                image_name="banner.png",
            )
            assert result["image_id"] == "img_002"
            mock_gateway.post.assert_called_once_with(
                "/file/image/ad/upload/",
                json_body={
                    "advertiser_id": "adv_123",
                    "upload_type": "UPLOAD_BY_URL",
                    "image_url": "https://example.com/image.png",
                    "file_name": "banner.png",
                },
            )


class TestGetImageInfo:
    @pytest.mark.asyncio
    async def test_get_image_info(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"image_id": "img_001", "width": 1920, "height": 1080},
                ]
            }
        }
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.get_image_info(
                workspace_id,
                mock_ad_account,
                image_ids=["img_001"],
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["width"] == 1920
            mock_gateway.get.assert_called_once_with(
                "/file/image/ad/info/",
                params={
                    "advertiser_id": "adv_123",
                    "image_ids": json.dumps(["img_001"]),
                },
            )


class TestSearchMusic:
    @pytest.mark.asyncio
    async def test_search_music_default_pagination(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"music_id": "m_001", "title": "Upbeat Track"},
                ]
            }
        }
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.search_music(
                workspace_id,
                mock_ad_account,
                query="upbeat",
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["title"] == "Upbeat Track"
            mock_gateway.get.assert_called_once_with(
                "/creative/music/search/",
                params={
                    "advertiser_id": "adv_123",
                    "query": "upbeat",
                    "page": "1",
                    "page_size": "20",
                },
            )

    @pytest.mark.asyncio
    async def test_search_music_custom_pagination(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            await service.search_music(
                workspace_id,
                mock_ad_account,
                query="chill",
                page=3,
                page_size=10,
            )
            mock_gateway.get.assert_called_once_with(
                "/creative/music/search/",
                params={
                    "advertiser_id": "adv_123",
                    "query": "chill",
                    "page": "3",
                    "page_size": "10",
                },
            )


class TestGetAdCreativeInfo:
    @pytest.mark.asyncio
    async def test_get_ad_creative_info(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"ad_id": "ad_001", "creative_type": "VIDEO"},
                    {"ad_id": "ad_002", "creative_type": "IMAGE"},
                ]
            }
        }
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.get_ad_creative_info(
                workspace_id,
                mock_ad_account,
                ad_ids=["ad_001", "ad_002"],
            )
            assert len(result["list"]) == 2
            assert result["list"][0]["creative_type"] == "VIDEO"
            mock_gateway.get.assert_called_once_with(
                "/creative/ads/info/",
                params={
                    "advertiser_id": "adv_123",
                    "ad_ids": json.dumps(["ad_001", "ad_002"]),
                },
            )

    @pytest.mark.asyncio
    async def test_get_ad_creative_info_single_id(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
        workspace_id: uuid.UUID,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"ad_id": "ad_solo", "creative_type": "IMAGE"},
                ]
            }
        }
        with patch.object(CreativeService, "_get_gateway", return_value=mock_gateway):
            service = CreativeService(mock_session)
            result = await service.get_ad_creative_info(
                workspace_id,
                mock_ad_account,
                ad_ids=["ad_solo"],
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["ad_id"] == "ad_solo"
            mock_gateway.get.assert_called_once_with(
                "/creative/ads/info/",
                params={
                    "advertiser_id": "adv_123",
                    "ad_ids": json.dumps(["ad_solo"]),
                },
            )
