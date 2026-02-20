import pytest

from backend.config import Settings


@pytest.mark.unit
class TestResearchConfig:
    def test_research_client_key_default_empty(self) -> None:
        s = Settings(
            secret_key="test",
            jwt_secret_key="test",
            token_vault_key="test",
        )
        assert s.tiktok_research_client_key == ""

    def test_research_client_secret_default_empty(self) -> None:
        s = Settings(
            secret_key="test",
            jwt_secret_key="test",
            token_vault_key="test",
        )
        assert s.tiktok_research_client_secret == ""
