"""Tests for content DB models - field assignment."""

import uuid
from datetime import datetime, timezone

import pytest

from backend.db.models.content import (
    ContentPublishJob,
    ContentSyncCursor,
)


class TestContentPublishJob:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()
        account_id = uuid.uuid4()

        job = ContentPublishJob()
        job.workspace_id = ws_id
        job.connected_account_id = account_id
        job.publish_id = "pub_12345"
        job.title = "Product Review Video"
        job.video_url = "https://cdn.tiktok.com/video/abc.mp4"
        job.privacy_level = "PUBLIC_TO_EVERYONE"
        job.status = "PENDING"
        job.platform_video_id = None
        job.error_message = None
        job.disable_duet = False
        job.disable_comment = True
        job.disable_stitch = False
        job.brand_content_toggle = True
        job.brand_organic_toggle = False

        assert job.workspace_id == ws_id
        assert job.connected_account_id == account_id
        assert job.publish_id == "pub_12345"
        assert job.title == "Product Review Video"
        assert job.video_url == "https://cdn.tiktok.com/video/abc.mp4"
        assert job.privacy_level == "PUBLIC_TO_EVERYONE"
        assert job.status == "PENDING"
        assert job.platform_video_id is None
        assert job.error_message is None
        assert job.disable_duet is False
        assert job.disable_comment is True
        assert job.disable_stitch is False
        assert job.brand_content_toggle is True
        assert job.brand_organic_toggle is False

    def test_published_job(self) -> None:
        job = ContentPublishJob()
        job.workspace_id = uuid.uuid4()
        job.connected_account_id = uuid.uuid4()
        job.publish_id = "pub_67890"
        job.status = "PUBLISHED"
        job.platform_video_id = "vid_final_99"

        assert job.status == "PUBLISHED"
        assert job.platform_video_id == "vid_final_99"

    def test_failed_job(self) -> None:
        job = ContentPublishJob()
        job.workspace_id = uuid.uuid4()
        job.connected_account_id = uuid.uuid4()
        job.publish_id = "pub_fail_001"
        job.status = "FAILED"
        job.error_message = "Upload timeout after 30s"

        assert job.status == "FAILED"
        assert job.error_message == "Upload timeout after 30s"


class TestContentSyncCursor:
    def test_fields(self) -> None:
        account_id = uuid.uuid4()
        last_sync = datetime(2026, 2, 19, 14, 0, tzinfo=timezone.utc)

        cursor = ContentSyncCursor()
        cursor.connected_account_id = account_id
        cursor.sync_type = "videos"
        cursor.cursor_value = "cursor_abc_123"
        cursor.last_sync_at = last_sync

        assert cursor.connected_account_id == account_id
        assert cursor.sync_type == "videos"
        assert cursor.cursor_value == "cursor_abc_123"
        assert cursor.last_sync_at == last_sync

    def test_video_metrics_sync_type(self) -> None:
        cursor = ContentSyncCursor()
        cursor.connected_account_id = uuid.uuid4()
        cursor.sync_type = "video_metrics"
        cursor.cursor_value = None

        assert cursor.sync_type == "video_metrics"
        assert cursor.cursor_value is None
        assert cursor.last_sync_at is None
