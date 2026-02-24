"""TikTok LIVE stream client wrapper."""

import enum
import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class LiveEventType(str, enum.Enum):
    COMMENT = "comment"
    GIFT = "gift"
    LIKE = "like"
    FOLLOW = "follow"
    SHARE = "share"
    JOIN = "join"
    LIVE_END = "live_end"


@dataclass(frozen=True)
class LiveEventData:
    event_type: LiveEventType
    user_id: str | None
    username: str | None
    payload: dict[str, Any]
    timestamp: datetime


class TikTokLiveClientWrapper:
    """Async wrapper for TikTokLive library with event callbacks."""

    def __init__(self, unique_id: str) -> None:
        self._unique_id = unique_id
        self._callbacks: dict[LiveEventType, list[Callable]] = {}
        self._connected = False
        self._room_id: str | None = None

    def on_event(self, event_type: LiveEventType, callback: Callable) -> None:
        """Register a callback for a specific event type."""
        self._callbacks.setdefault(event_type, []).append(callback)

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def room_id(self) -> str | None:
        return self._room_id

    async def connect(self) -> None:
        """Connect to LIVE stream. Requires TikTokLive package."""
        try:
            from TikTokLive import TikTokLiveClient
            from TikTokLive.events import (
                CommentEvent,
                ConnectEvent,
                DisconnectEvent,
                FollowEvent,
                GiftEvent,
                JoinEvent,
                LikeEvent,
                LiveEndEvent,
                ShareEvent,
            )
        except ImportError:
            raise NotImplementedError(
                "TikTokLive package not installed. Run: pip install TikTokLive"
            )

        client = TikTokLiveClient(unique_id=self._unique_id)

        @client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent) -> None:
            self._connected = True
            self._room_id = str(client.room_id) if client.room_id else None
            logger.info(
                "Connected to LIVE: %s (room %s)", self._unique_id, self._room_id
            )

        @client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent) -> None:
            self._connected = False

        @client.on(CommentEvent)
        async def on_comment(event: CommentEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.COMMENT,
                    user_id=str(event.user.user_id) if event.user else None,
                    username=event.user.nickname if event.user else None,
                    payload={"comment": event.comment},
                    timestamp=datetime.now(UTC),
                )
            )

        @client.on(GiftEvent)
        async def on_gift(event: GiftEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.GIFT,
                    user_id=str(event.user.user_id) if event.user else None,
                    username=event.user.nickname if event.user else None,
                    payload={
                        "gift_name": event.gift.name if event.gift else "unknown",
                        "repeat_count": event.repeat_count,
                    },
                    timestamp=datetime.now(UTC),
                )
            )

        @client.on(LikeEvent)
        async def on_like(event: LikeEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.LIKE,
                    user_id=str(event.user.user_id) if event.user else None,
                    username=event.user.nickname if event.user else None,
                    payload={},
                    timestamp=datetime.now(UTC),
                )
            )

        @client.on(FollowEvent)
        async def on_follow(event: FollowEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.FOLLOW,
                    user_id=str(event.user.user_id) if event.user else None,
                    username=event.user.nickname if event.user else None,
                    payload={},
                    timestamp=datetime.now(UTC),
                )
            )

        @client.on(ShareEvent)
        async def on_share(event: ShareEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.SHARE,
                    user_id=str(event.user.user_id) if event.user else None,
                    username=event.user.nickname if event.user else None,
                    payload={},
                    timestamp=datetime.now(UTC),
                )
            )

        @client.on(JoinEvent)
        async def on_join(event: JoinEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.JOIN,
                    user_id=str(event.user.user_id) if event.user else None,
                    username=event.user.nickname if event.user else None,
                    payload={},
                    timestamp=datetime.now(UTC),
                )
            )

        @client.on(LiveEndEvent)
        async def on_live_end(event: LiveEndEvent) -> None:
            await self._dispatch(
                LiveEventData(
                    event_type=LiveEventType.LIVE_END,
                    user_id=None,
                    username=None,
                    payload={},
                    timestamp=datetime.now(UTC),
                )
            )
            self._connected = False

        await client.start()

    async def _dispatch(self, event: LiveEventData) -> None:
        """Dispatch event to registered callbacks."""
        for callback in self._callbacks.get(event.event_type, []):
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception:
                logger.exception("Error in callback for %s", event.event_type)
