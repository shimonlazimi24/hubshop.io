"""Tests for LIVE DB models."""

from backend.db.models.live import (
    LiveAnalytics,
    LiveEvent,
    LiveEventType,
    LiveSession,
    SessionStatus,
)


class TestSessionStatusEnum:
    """Test SessionStatus enum values."""

    def test_monitoring_value(self) -> None:
        assert SessionStatus.MONITORING.value == "monitoring"

    def test_ended_value(self) -> None:
        assert SessionStatus.ENDED.value == "ended"

    def test_error_value(self) -> None:
        assert SessionStatus.ERROR.value == "error"

    def test_member_count(self) -> None:
        assert len(SessionStatus) == 3


class TestLiveEventTypeEnum:
    """Test LiveEventType enum values."""

    def test_comment_value(self) -> None:
        assert LiveEventType.COMMENT.value == "comment"

    def test_gift_value(self) -> None:
        assert LiveEventType.GIFT.value == "gift"

    def test_like_value(self) -> None:
        assert LiveEventType.LIKE.value == "like"

    def test_follow_value(self) -> None:
        assert LiveEventType.FOLLOW.value == "follow"

    def test_share_value(self) -> None:
        assert LiveEventType.SHARE.value == "share"

    def test_join_value(self) -> None:
        assert LiveEventType.JOIN.value == "join"

    def test_live_end_value(self) -> None:
        assert LiveEventType.LIVE_END.value == "live_end"

    def test_commerce_value(self) -> None:
        assert LiveEventType.COMMERCE.value == "commerce"

    def test_member_count(self) -> None:
        assert len(LiveEventType) == 8


class TestLiveSession:
    """Test LiveSession model schema."""

    def test_tablename(self) -> None:
        assert LiveSession.__tablename__ == "live_sessions"

    def test_columns(self) -> None:
        columns = LiveSession.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "unique_id",
            "room_id",
            "status",
            "started_at",
            "ended_at",
            "error_message",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_composite_index(self) -> None:
        indexes = LiveSession.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_live_sessions_workspace_status" in index_names


class TestLiveEvent:
    """Test LiveEvent model schema."""

    def test_tablename(self) -> None:
        assert LiveEvent.__tablename__ == "live_events"

    def test_columns(self) -> None:
        columns = LiveEvent.__table__.columns.keys()
        expected = [
            "id",
            "session_id",
            "event_type",
            "user_id",
            "username",
            "payload",
            "timestamp",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_no_timestamp_mixin_columns(self) -> None:
        """LiveEvent should NOT have created_at/updated_at from TimestampMixin."""
        columns = LiveEvent.__table__.columns.keys()
        assert "created_at" not in columns
        assert "updated_at" not in columns

    def test_has_event_type_index(self) -> None:
        indexes = LiveEvent.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_live_events_session_event_type" in index_names

    def test_has_timestamp_index(self) -> None:
        indexes = LiveEvent.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_live_events_session_timestamp" in index_names


class TestLiveAnalytics:
    """Test LiveAnalytics model schema."""

    def test_tablename(self) -> None:
        assert LiveAnalytics.__tablename__ == "live_analytics"

    def test_columns(self) -> None:
        columns = LiveAnalytics.__table__.columns.keys()
        expected = [
            "id",
            "session_id",
            "total_viewers",
            "peak_concurrent",
            "total_comments",
            "total_likes",
            "total_shares",
            "total_follows",
            "gift_revenue",
            "engagement_rate",
            "top_commenters",
            "top_gifters",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_session_id_unique(self) -> None:
        """session_id should have a unique constraint."""
        col = LiveAnalytics.__table__.columns["session_id"]
        assert col.unique is True
