from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.auth.social import SocialAuthService
from backend.db.models.organization import Role
from backend.db.models.social_identity import SocialIdentity, SocialProvider
from backend.db.models.user import User


def _make_mock_db() -> AsyncMock:
    """Return an AsyncMock that behaves like an AsyncSession."""
    db = AsyncMock()
    db.add = MagicMock()
    return db


def _make_user(user_id: uuid.UUID | None = None, email: str = "u@example.com") -> User:
    user = User(
        email=email,
        full_name="Test User",
        hashed_password=None,
    )
    user.id = user_id or uuid.uuid4()
    return user


def _make_identity(user: User, provider: SocialProvider = SocialProvider.TIKTOK) -> SocialIdentity:
    identity = SocialIdentity(
        user_id=user.id,
        provider=provider.value,
        provider_user_id="ext_123",
        email=user.email,
        display_name=user.full_name,
    )
    identity.user = user
    return identity


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetOrCreateUserNew:
    """When no existing social identity is found AND no user with matching email."""

    @pytest.mark.asyncio
    async def test_creates_new_user_org_workspace_membership_identity(self) -> None:
        db = _make_mock_db()

        # First query (identity lookup) -> None
        identity_result = MagicMock()
        identity_result.scalar_one_or_none.return_value = None

        # Second query (user by email) -> None
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None

        db.execute.side_effect = [identity_result, user_result]

        # Make flush assign a UUID to the user
        user_id = uuid.uuid4()

        async def _flush_side_effect() -> None:
            for call in db.add.call_args_list:
                obj = call[0][0]
                if isinstance(obj, User) and not hasattr(obj, "id") or getattr(obj, "id", None) is None:
                    obj.id = user_id

        db.flush.side_effect = _flush_side_effect

        svc = SocialAuthService(db)
        user, is_new = await svc.get_or_create_user(
            provider=SocialProvider.GOOGLE,
            provider_user_id="google_999",
            email="john@acme.com",
            display_name="John",
            avatar_url="https://img.example.com/j.png",
        )

        assert is_new is True
        assert user.email == "john@acme.com"
        assert user.full_name == "John"

        added_types = [type(call[0][0]).__name__ for call in db.add.call_args_list]
        assert "User" in added_types
        assert "Organization" in added_types
        assert "Workspace" in added_types
        assert "Membership" in added_types
        assert "SocialIdentity" in added_types
        assert db.flush.await_count == 3  # user, org, workspace


@pytest.mark.unit
class TestGetOrCreateUserExisting:
    """When an existing social identity is found."""

    @pytest.mark.asyncio
    async def test_returns_existing_user_is_new_false(self) -> None:
        db = _make_mock_db()

        user = _make_user(email="existing@acme.com")
        identity = _make_identity(user)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = identity
        db.execute.return_value = result_mock

        svc = SocialAuthService(db)
        returned_user, is_new = await svc.get_or_create_user(
            provider=SocialProvider.TIKTOK,
            provider_user_id="ext_123",
            email="existing@acme.com",
        )

        assert is_new is False
        assert returned_user is user
        # Only one execute call (identity lookup), no user lookup needed
        db.execute.assert_awaited_once()


@pytest.mark.unit
class TestGetOrCreateUserLinkExisting:
    """When no identity but user with same email exists -> link, not create."""

    @pytest.mark.asyncio
    async def test_links_identity_to_existing_user(self) -> None:
        db = _make_mock_db()

        existing_user = _make_user(email="link@acme.com")

        identity_result = MagicMock()
        identity_result.scalar_one_or_none.return_value = None

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = existing_user

        db.execute.side_effect = [identity_result, user_result]

        svc = SocialAuthService(db)
        user, is_new = await svc.get_or_create_user(
            provider=SocialProvider.GOOGLE,
            provider_user_id="google_456",
            email="link@acme.com",
        )

        assert is_new is False
        assert user is existing_user
        # Only SocialIdentity should be added (no User, Org, etc.)
        added_types = [type(call[0][0]).__name__ for call in db.add.call_args_list]
        assert added_types == ["SocialIdentity"]


@pytest.mark.unit
class TestOrgNameFromEmail:
    def test_acme(self) -> None:
        assert SocialAuthService._org_name_from_email("john@acme.com") == "acme"

    def test_gmail(self) -> None:
        assert SocialAuthService._org_name_from_email("test@gmail.com") == "gmail"

    def test_subdomain(self) -> None:
        assert SocialAuthService._org_name_from_email("a@mail.example.co.uk") == "mail"

    def test_no_at_sign(self) -> None:
        # Edge case: no @ in the string
        assert SocialAuthService._org_name_from_email("plaintext") == "plaintext"


@pytest.mark.unit
class TestBuildTiktokAuthorizeUrl:
    def test_url_structure(self) -> None:
        url = SocialAuthService.build_tiktok_login_url(state="abc123")
        assert "https://www.tiktok.com/v2/auth/authorize/" in url
        assert "user.info.basic" in url
        assert "state=abc123" in url
        assert "response_type=code" in url

    def test_state_included(self) -> None:
        url = SocialAuthService.build_tiktok_login_url(state="xyz")
        assert "state=xyz" in url


@pytest.mark.unit
class TestBuildGoogleAuthorizeUrl:
    def test_url_structure(self) -> None:
        url = SocialAuthService.build_google_login_url(state="def456")
        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert "state=def456" in url
        assert "scope=openid" in url
        assert "access_type=offline" in url
        assert "prompt=consent" in url

    def test_state_included(self) -> None:
        url = SocialAuthService.build_google_login_url(state="mystate")
        assert "state=mystate" in url
