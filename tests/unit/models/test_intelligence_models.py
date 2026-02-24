"""Tests for intelligence DB models."""

from backend.db.models.intelligence import (
    CompetitorContent,
    CompetitorTracker,
    ResearchQuery,
    TrendSnapshot,
    TrendType,
)


class TestTrendTypeEnum:
    """Test TrendType enum values."""

    def test_hashtag_value(self) -> None:
        assert TrendType.HASHTAG.value == "hashtag"

    def test_sound_value(self) -> None:
        assert TrendType.SOUND.value == "sound"

    def test_product_value(self) -> None:
        assert TrendType.PRODUCT.value == "product"

    def test_member_count(self) -> None:
        assert len(TrendType) == 3


class TestTrendSnapshot:
    """Test TrendSnapshot model schema."""

    def test_tablename(self) -> None:
        assert TrendSnapshot.__tablename__ == "trend_snapshots"

    def test_columns(self) -> None:
        columns = TrendSnapshot.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "trend_type",
            "name",
            "engagement_score",
            "region",
            "metadata_json",
            "captured_at",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_composite_index(self) -> None:
        indexes = TrendSnapshot.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_trend_snapshots_workspace_type_captured" in index_names


class TestCompetitorTracker:
    """Test CompetitorTracker model schema."""

    def test_tablename(self) -> None:
        assert CompetitorTracker.__tablename__ == "competitor_trackers"

    def test_columns(self) -> None:
        columns = CompetitorTracker.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "username",
            "display_name",
            "platform_user_id",
            "profile_data",
            "last_synced_at",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_unique_index(self) -> None:
        indexes = CompetitorTracker.__table__.indexes
        unique_indexes = {idx.name for idx in indexes if idx.unique}
        assert "ix_competitor_trackers_workspace_username" in unique_indexes


class TestCompetitorContent:
    """Test CompetitorContent model schema."""

    def test_tablename(self) -> None:
        assert CompetitorContent.__tablename__ == "competitor_content"

    def test_columns(self) -> None:
        columns = CompetitorContent.__table__.columns.keys()
        expected = [
            "id",
            "tracker_id",
            "video_id",
            "description",
            "metrics",
            "hashtags",
            "published_at",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_unique_index(self) -> None:
        indexes = CompetitorContent.__table__.indexes
        unique_indexes = {idx.name for idx in indexes if idx.unique}
        assert "ix_competitor_content_tracker_video" in unique_indexes


class TestResearchQuery:
    """Test ResearchQuery model schema."""

    def test_tablename(self) -> None:
        assert ResearchQuery.__tablename__ == "research_queries"

    def test_columns(self) -> None:
        columns = ResearchQuery.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "name",
            "query_params",
            "last_run_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"
