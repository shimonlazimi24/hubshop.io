import pytest

from backend.db.models.platform import Platform


@pytest.mark.unit
class TestPlatformEnum:
    def test_research_platform_exists(self) -> None:
        assert Platform.RESEARCH == "research"

    def test_all_five_platforms(self) -> None:
        platforms = {p.value for p in Platform}
        assert platforms == {"shop", "developer", "marketing", "live", "research"}
