import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.tiktok.live.client import (
    LiveEventData,
    LiveEventType,
    TikTokLiveClientWrapper,
)


@pytest.mark.unit
class TestLiveEventType:
    def test_comment(self) -> None:
        assert LiveEventType.COMMENT == "comment"

    def test_gift(self) -> None:
        assert LiveEventType.GIFT == "gift"

    def test_like(self) -> None:
        assert LiveEventType.LIKE == "like"

    def test_follow(self) -> None:
        assert LiveEventType.FOLLOW == "follow"

    def test_share(self) -> None:
        assert LiveEventType.SHARE == "share"

    def test_join(self) -> None:
        assert LiveEventType.JOIN == "join"

    def test_live_end(self) -> None:
        assert LiveEventType.LIVE_END == "live_end"

    def test_all_event_types(self) -> None:
        values = {e.value for e in LiveEventType}
        assert values == {"comment", "gift", "like", "follow", "share", "join", "live_end"}


@pytest.mark.unit
class TestLiveEventData:
    def test_frozen_dataclass(self) -> None:
        event = LiveEventData(
            event_type=LiveEventType.COMMENT,
            user_id="123",
            username="testuser",
            payload={"comment": "hello"},
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert event.event_type == LiveEventType.COMMENT
        assert event.user_id == "123"
        assert event.username == "testuser"
        assert event.payload == {"comment": "hello"}
        with pytest.raises(AttributeError):
            event.user_id = "456"  # type: ignore[misc]


@pytest.mark.unit
class TestTikTokLiveClientWrapper:
    def test_init(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        assert wrapper._unique_id == "@testuser"
        assert wrapper._callbacks == {}
        assert wrapper.connected is False
        assert wrapper.room_id is None

    def test_register_callback(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        callback = MagicMock()
        wrapper.on_event(LiveEventType.COMMENT, callback)
        assert LiveEventType.COMMENT in wrapper._callbacks
        assert callback in wrapper._callbacks[LiveEventType.COMMENT]

    def test_register_multiple_callbacks(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        cb1, cb2 = MagicMock(), MagicMock()
        wrapper.on_event(LiveEventType.GIFT, cb1)
        wrapper.on_event(LiveEventType.GIFT, cb2)
        assert len(wrapper._callbacks[LiveEventType.GIFT]) == 2

    def test_register_callbacks_different_events(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        cb1, cb2 = MagicMock(), MagicMock()
        wrapper.on_event(LiveEventType.COMMENT, cb1)
        wrapper.on_event(LiveEventType.GIFT, cb2)
        assert len(wrapper._callbacks) == 2

    @pytest.mark.asyncio
    async def test_dispatch_sync_callback(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        callback = MagicMock()
        wrapper.on_event(LiveEventType.COMMENT, callback)
        event = LiveEventData(
            event_type=LiveEventType.COMMENT,
            user_id="1",
            username="user",
            payload={"comment": "hi"},
            timestamp=datetime.now(timezone.utc),
        )
        await wrapper._dispatch(event)
        callback.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_dispatch_async_callback(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        callback = AsyncMock()
        wrapper.on_event(LiveEventType.LIKE, callback)
        event = LiveEventData(
            event_type=LiveEventType.LIKE,
            user_id="1",
            username="user",
            payload={},
            timestamp=datetime.now(timezone.utc),
        )
        await wrapper._dispatch(event)
        callback.assert_awaited_once_with(event)

    @pytest.mark.asyncio
    async def test_dispatch_no_callbacks(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        event = LiveEventData(
            event_type=LiveEventType.FOLLOW,
            user_id="1",
            username="user",
            payload={},
            timestamp=datetime.now(timezone.utc),
        )
        # Should not raise
        await wrapper._dispatch(event)

    @pytest.mark.asyncio
    async def test_dispatch_callback_exception_handled(self) -> None:
        wrapper = TikTokLiveClientWrapper(unique_id="@testuser")
        bad_callback = MagicMock(side_effect=ValueError("boom"))
        good_callback = MagicMock()
        wrapper.on_event(LiveEventType.JOIN, bad_callback)
        wrapper.on_event(LiveEventType.JOIN, good_callback)
        event = LiveEventData(
            event_type=LiveEventType.JOIN,
            user_id="1",
            username="user",
            payload={},
            timestamp=datetime.now(timezone.utc),
        )
        # Should not raise, and the second callback should still be called
        await wrapper._dispatch(event)
        bad_callback.assert_called_once()
        good_callback.assert_called_once()
