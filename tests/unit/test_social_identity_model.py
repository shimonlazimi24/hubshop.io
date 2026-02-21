import uuid

import pytest

from backend.db.models.social_identity import SocialIdentity, SocialProvider


@pytest.mark.unit
class TestSocialProviderEnum:
    def test_tiktok_value(self) -> None:
        assert SocialProvider.TIKTOK == "tiktok"
        assert SocialProvider.TIKTOK.value == "tiktok"

    def test_google_value(self) -> None:
        assert SocialProvider.GOOGLE == "google"
        assert SocialProvider.GOOGLE.value == "google"

    def test_all_providers(self) -> None:
        providers = {p.value for p in SocialProvider}
        assert providers == {"tiktok", "google"}


@pytest.mark.unit
class TestSocialIdentityModel:
    def test_tablename(self) -> None:
        assert SocialIdentity.__tablename__ == "social_identities"

    def test_instantiation_all_fields(self) -> None:
        user_id = uuid.uuid4()
        identity = SocialIdentity(
            id=uuid.uuid4(),
            user_id=user_id,
            provider=SocialProvider.TIKTOK.value,
            provider_user_id="tiktok_12345",
            email="user@example.com",
            display_name="Test User",
            avatar_url="https://example.com/avatar.png",
        )
        assert identity.user_id == user_id
        assert identity.provider == SocialProvider.TIKTOK.value
        assert identity.provider_user_id == "tiktok_12345"
        assert identity.email == "user@example.com"
        assert identity.display_name == "Test User"
        assert identity.avatar_url == "https://example.com/avatar.png"

    def test_instantiation_nullable_fields(self) -> None:
        identity = SocialIdentity(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            provider=SocialProvider.GOOGLE.value,
            provider_user_id="google_67890",
        )
        assert identity.provider == SocialProvider.GOOGLE.value
        assert identity.provider_user_id == "google_67890"
        assert identity.email is None
        assert identity.display_name is None
        assert identity.avatar_url is None

    def test_unique_constraint_defined(self) -> None:
        constraints = [
            c.name
            for c in SocialIdentity.__table__.constraints
            if hasattr(c, "name") and c.name is not None
        ]
        assert "uq_social_provider_user" in constraints
