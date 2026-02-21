# Phase 0: Auth Overhaul + Connect Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace developer-focused auth with production-grade social login (TikTok, Google, email) and redesign the Connect pipeline with full OAuth scopes, onboarding sync, and sync status dashboard.

**Architecture:** Add a `SocialIdentity` model to link providers to users. Add TikTok/Google OAuth login endpoints. Expand Connect scopes to full platform access. Add post-connect initial sync with progress tracking. Redesign frontend login/register and connect pages.

**Tech Stack:** FastAPI, SQLAlchemy async, httpx, python-jose (JWT), Next.js 15, TypeScript, Tailwind CSS

---

## Task 1: Add SocialIdentity DB Model

**Files:**
- Create: `backend/db/models/social_identity.py`
- Modify: `backend/db/models/__init__.py`
- Modify: `backend/db/models/user.py` (add relationship + make password nullable)
- Test: `tests/unit/test_social_identity_model.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_social_identity_model.py
import uuid
import pytest
from backend.db.models.social_identity import SocialIdentity, SocialProvider


class TestSocialIdentityModel:
    def test_social_provider_enum_values(self):
        assert SocialProvider.TIKTOK.value == "tiktok"
        assert SocialProvider.GOOGLE.value == "google"

    def test_social_identity_fields(self):
        identity = SocialIdentity(
            user_id=uuid.uuid4(),
            provider=SocialProvider.TIKTOK,
            provider_user_id="open_id_123",
            email="user@example.com",
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg",
        )
        assert identity.provider == SocialProvider.TIKTOK
        assert identity.provider_user_id == "open_id_123"
        assert identity.email == "user@example.com"

    def test_social_identity_nullable_fields(self):
        identity = SocialIdentity(
            user_id=uuid.uuid4(),
            provider=SocialProvider.GOOGLE,
            provider_user_id="google_123",
        )
        assert identity.email is None
        assert identity.display_name is None
        assert identity.avatar_url is None
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_identity_model.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.db.models.social_identity'`

**Step 3: Write the model**

```python
# backend/db/models/social_identity.py
import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class SocialProvider(str, enum.Enum):
    TIKTOK = "tiktok"
    GOOGLE = "google"


class SocialIdentity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "social_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[SocialProvider] = mapped_column(
        Enum(SocialProvider, name="social_provider_enum"),
        nullable=False,
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ID from the social provider (open_id for TikTok, sub for Google)",
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    user: Mapped["User"] = relationship(back_populates="social_identities")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_social_provider_user"),
    )
```

**Step 4: Update User model — make hashed_password nullable, add relationship**

```python
# backend/db/models/user.py — changes:
# Line 11: Change nullable=False to nullable=True for hashed_password
hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

# Add after memberships relationship (line 19):
social_identities: Mapped[list["SocialIdentity"]] = relationship(  # noqa: F821
    back_populates="user",
    lazy="selectin",
)
```

**Step 5: Update `__init__.py` — add SocialIdentity exports**

Add to `backend/db/models/__init__.py`:
```python
from backend.db.models.social_identity import SocialIdentity, SocialProvider
```
And add `"SocialIdentity"`, `"SocialProvider"` to `__all__`.

**Step 6: Run tests to verify they pass**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_identity_model.py -v`
Expected: PASS (3 tests)

**Step 7: Commit**

```bash
git add backend/db/models/social_identity.py backend/db/models/__init__.py backend/db/models/user.py tests/unit/test_social_identity_model.py
git commit -m "feat: add SocialIdentity model for TikTok/Google social login"
```

---

## Task 2: Add Google OAuth Config Settings

**Files:**
- Modify: `backend/config.py`
- Modify: `tests/conftest.py`
- Test: `tests/unit/test_social_config.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_social_config.py
from backend.config import settings


class TestSocialConfig:
    def test_google_oauth_settings_exist(self):
        assert hasattr(settings, "google_client_id")
        assert hasattr(settings, "google_client_secret")
        assert hasattr(settings, "google_redirect_uri")

    def test_tiktok_login_redirect_uri_exists(self):
        assert hasattr(settings, "tiktok_login_redirect_uri")
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_config.py -v`
Expected: FAIL — `AssertionError`

**Step 3: Add settings**

Add to `backend/config.py` inside `Settings` class (after line 52):
```python
    # Google OAuth (for social login)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # TikTok Login (social login — distinct from Developer platform connect)
    tiktok_login_redirect_uri: str = "http://localhost:8000/api/auth/tiktok/callback"
```

**Step 4: Add to test conftest**

Add to `tests/conftest.py`:
```python
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_google_client_id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_google_secret")
```

**Step 5: Run tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_config.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/config.py tests/conftest.py tests/unit/test_social_config.py
git commit -m "feat: add Google OAuth and TikTok login config settings"
```

---

## Task 3: Add Social Auth Service (backend/auth/social.py)

**Files:**
- Create: `backend/auth/social.py`
- Test: `tests/unit/test_social_auth_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_social_auth_service.py
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.auth.social import SocialAuthService
from backend.db.models.social_identity import SocialProvider


class TestSocialAuthService:
    @pytest.mark.asyncio
    async def test_get_or_create_user_creates_new_user(self):
        """First social login creates a new user + org + workspace + membership."""
        mock_db = AsyncMock()
        # Simulate no existing social identity found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.flush = AsyncMock()

        service = SocialAuthService(mock_db)
        user, is_new = await service.get_or_create_user(
            provider=SocialProvider.TIKTOK,
            provider_user_id="open_id_123",
            email="test@example.com",
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg",
        )

        assert is_new is True
        # Verify db.add was called (for user, org, workspace, membership, identity)
        assert mock_db.add.call_count >= 4

    @pytest.mark.asyncio
    async def test_get_or_create_user_returns_existing(self):
        """Second social login returns existing user."""
        mock_db = AsyncMock()
        mock_identity = MagicMock()
        mock_identity.user = MagicMock()
        mock_identity.user.id = uuid.uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_identity
        mock_db.execute.return_value = mock_result

        service = SocialAuthService(mock_db)
        user, is_new = await service.get_or_create_user(
            provider=SocialProvider.GOOGLE,
            provider_user_id="google_456",
            email="existing@example.com",
        )

        assert is_new is False
        assert user == mock_identity.user

    def test_generate_org_name_from_email(self):
        service = SocialAuthService(None)  # type: ignore
        assert service._org_name_from_email("john@acme.com") == "acme"
        assert service._org_name_from_email("test@gmail.com") == "test"

    def test_build_tiktok_authorize_url(self):
        url = SocialAuthService.build_tiktok_login_url(state="random-state")
        assert "www.tiktok.com" in url
        assert "user.info.basic" in url
        assert "random-state" in url

    def test_build_google_authorize_url(self):
        url = SocialAuthService.build_google_login_url(state="random-state")
        assert "accounts.google.com" in url
        assert "random-state" in url
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_auth_service.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement the service**

```python
# backend/auth/social.py
from __future__ import annotations

import uuid
from urllib.parse import urlencode

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.db.models.organization import Membership, Organization, Role, Workspace
from backend.db.models.social_identity import SocialIdentity, SocialProvider
from backend.db.models.user import User


class SocialAuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_or_create_user(
        self,
        *,
        provider: SocialProvider,
        provider_user_id: str,
        email: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> tuple[User, bool]:
        """Find existing user by social identity or create a new one.

        Returns (user, is_new_user).
        """
        # Check if this social identity already exists
        result = await self._db.execute(
            select(SocialIdentity)
            .options(selectinload(SocialIdentity.user))
            .where(
                SocialIdentity.provider == provider,
                SocialIdentity.provider_user_id == provider_user_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing.user, False

        # Check if a user with this email already exists (link identity)
        user: User | None = None
        if email:
            result = await self._db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

        is_new = user is None
        if is_new:
            org_name = self._org_name_from_email(email) if email else "My Organization"
            user = User(
                email=email or f"{provider.value}_{provider_user_id}@frodo.local",
                full_name=display_name or "Frodo User",
                hashed_password=None,
            )
            self._db.add(user)
            await self._db.flush()

            slug = org_name.lower().replace(" ", "-")[:50]
            org = Organization(name=org_name, slug=f"{slug}-{str(user.id)[:8]}")
            self._db.add(org)
            await self._db.flush()

            workspace = Workspace(name="Default", slug="default", organization_id=org.id)
            self._db.add(workspace)
            await self._db.flush()

            membership = Membership(
                user_id=user.id,
                organization_id=org.id,
                workspace_id=workspace.id,
                role=Role.OWNER,
            )
            self._db.add(membership)

        # Create the social identity link
        identity = SocialIdentity(
            user_id=user.id,  # type: ignore[union-attr]
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        self._db.add(identity)

        return user, is_new  # type: ignore[return-value]

    @staticmethod
    def _org_name_from_email(email: str) -> str:
        domain = email.split("@")[1] if "@" in email else email
        name = domain.split(".")[0]
        return name

    @staticmethod
    def build_tiktok_login_url(state: str) -> str:
        params = {
            "client_key": settings.tiktok_developer_client_key,
            "response_type": "code",
            "scope": "user.info.basic,user.info.profile",
            "redirect_uri": settings.tiktok_login_redirect_uri,
            "state": state,
        }
        return f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(params)}"

    @staticmethod
    def build_google_login_url(state: str) -> str:
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
```

**Step 4: Run tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_auth_service.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add backend/auth/social.py tests/unit/test_social_auth_service.py
git commit -m "feat: add SocialAuthService for TikTok/Google login"
```

---

## Task 4: Add Social Auth Routes (TikTok + Google login endpoints)

**Files:**
- Modify: `backend/auth/routes.py`
- Test: `tests/unit/test_social_auth_routes.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_social_auth_routes.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSocialAuthRoutes:
    def test_tiktok_login_url_endpoint_exists(self):
        """GET /api/auth/tiktok/login returns authorize URL."""
        from backend.auth.routes import router
        routes = [r.path for r in router.routes]
        assert "/tiktok/login" in routes

    def test_google_login_url_endpoint_exists(self):
        """GET /api/auth/google/login returns authorize URL."""
        from backend.auth.routes import router
        routes = [r.path for r in router.routes]
        assert "/google/login" in routes

    def test_tiktok_callback_endpoint_exists(self):
        """GET /api/auth/tiktok/callback exists."""
        from backend.auth.routes import router
        routes = [r.path for r in router.routes]
        assert "/tiktok/callback" in routes

    def test_google_callback_endpoint_exists(self):
        """GET /api/auth/google/callback exists."""
        from backend.auth.routes import router
        routes = [r.path for r in router.routes]
        assert "/google/callback" in routes
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_auth_routes.py -v`
Expected: FAIL

**Step 3: Add social auth routes to `backend/auth/routes.py`**

Add after the existing `/me` endpoint (after line 170):

```python
# ─── Social Login: TikTok ────────────────────────────────────────────────────


class SocialLoginResponse(BaseModel):
    authorize_url: str


@router.get("/tiktok/login", response_model=SocialLoginResponse)
async def tiktok_login() -> SocialLoginResponse:
    """Generate TikTok OAuth URL for social login (identity only)."""
    state = str(uuid.uuid4())
    from backend.auth.social import SocialAuthService
    url = SocialAuthService.build_tiktok_login_url(state=state)
    return SocialLoginResponse(authorize_url=url)


@router.get("/tiktok/callback")
async def tiktok_callback(
    code: str = Query(...),
    state: str = Query(""),
    db: DBSession = ...,  # type: ignore[assignment]
) -> TokenResponse:
    """Handle TikTok social login callback. Exchange code, create/find user, return JWT."""
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": settings.tiktok_developer_client_key,
                "client_secret": settings.tiktok_developer_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.tiktok_login_redirect_uri,
            },
        )
        resp.raise_for_status()
        token_data = resp.json()

    if "access_token" not in token_data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TikTok login failed: {token_data.get('error_description', 'Unknown error')}",
        )

    # Fetch user info
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://open.tiktokapis.com/v2/user/info/",
            params={"fields": "open_id,display_name,avatar_url"},
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        resp.raise_for_status()
        user_info = resp.json().get("data", {}).get("user", {})

    from backend.auth.social import SocialAuthService
    from backend.db.models.social_identity import SocialProvider

    service = SocialAuthService(db)
    user, _ = await service.get_or_create_user(
        provider=SocialProvider.TIKTOK,
        provider_user_id=token_data.get("open_id", ""),
        display_name=user_info.get("display_name"),
        avatar_url=user_info.get("avatar_url"),
    )

    # Get membership for JWT
    membership_result = await db.execute(
        select(Membership).where(Membership.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            membership.organization_id if membership else None,
            membership.role.value if membership else None,
        ),
        refresh_token=create_refresh_token(user.id),
    )


# ─── Social Login: Google ─────────────────────────────────────────────────────


@router.get("/google/login", response_model=SocialLoginResponse)
async def google_login() -> SocialLoginResponse:
    """Generate Google OAuth URL for social login."""
    state = str(uuid.uuid4())
    from backend.auth.social import SocialAuthService
    url = SocialAuthService.build_google_login_url(state=state)
    return SocialLoginResponse(authorize_url=url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(""),
    db: DBSession = ...,  # type: ignore[assignment]
) -> TokenResponse:
    """Handle Google social login callback."""
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
        )
        resp.raise_for_status()
        token_data = resp.json()

    if "access_token" not in token_data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google login failed",
        )

    # Fetch user info
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        resp.raise_for_status()
        user_info = resp.json()

    from backend.auth.social import SocialAuthService
    from backend.db.models.social_identity import SocialProvider

    service = SocialAuthService(db)
    user, _ = await service.get_or_create_user(
        provider=SocialProvider.GOOGLE,
        provider_user_id=user_info.get("id", ""),
        email=user_info.get("email"),
        display_name=user_info.get("name"),
        avatar_url=user_info.get("picture"),
    )

    membership_result = await db.execute(
        select(Membership).where(Membership.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            membership.organization_id if membership else None,
            membership.role.value if membership else None,
        ),
        refresh_token=create_refresh_token(user.id),
    )
```

Also add these imports at the top of `backend/auth/routes.py`:
```python
import httpx
from fastapi import Query
from backend.config import settings
```

**Step 4: Run tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_social_auth_routes.py -v`
Expected: PASS (4 tests)

**Step 5: Run full auth test suite to check for regressions**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_jwt.py tests/unit/test_passwords.py -v`
Expected: All existing tests PASS

**Step 6: Commit**

```bash
git add backend/auth/routes.py tests/unit/test_social_auth_routes.py
git commit -m "feat: add TikTok and Google social login endpoints"
```

---

## Task 5: Expand OAuth Scopes in Connect Routes

**Files:**
- Modify: `backend/modules/connect/routes.py`
- Test: `tests/unit/test_connect_scopes.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_connect_scopes.py
import pytest


class TestConnectScopes:
    def test_developer_scopes_include_publish(self):
        """Developer OAuth should request video.publish and comment scopes."""
        from backend.modules.connect.routes import DEVELOPER_SCOPES
        assert "video.publish" in DEVELOPER_SCOPES
        assert "video.upload" in DEVELOPER_SCOPES
        assert "comment.list" in DEVELOPER_SCOPES
        assert "user.info.stats" in DEVELOPER_SCOPES

    def test_developer_scopes_is_comma_separated_string(self):
        from backend.modules.connect.routes import DEVELOPER_SCOPES
        # Should be usable as-is in OAuth URL
        assert "," in DEVELOPER_SCOPES
        assert " " not in DEVELOPER_SCOPES
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_connect_scopes.py -v`
Expected: FAIL — `ImportError: cannot import name 'DEVELOPER_SCOPES'`

**Step 3: Add scope constants and update routes**

Add near the top of `backend/modules/connect/routes.py` (after imports):

```python
# Full production scopes for each platform connection
DEVELOPER_SCOPES = (
    "user.info.basic,"
    "user.info.profile,"
    "user.info.stats,"
    "video.list,"
    "video.publish,"
    "video.upload,"
    "comment.list,"
    "comment.list.manage"
)
```

Update `developer_authorize` (line 128) to use the constant:
```python
"scope": DEVELOPER_SCOPES,
```

**Step 4: Run tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_connect_scopes.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/connect/routes.py tests/unit/test_connect_scopes.py
git commit -m "feat: expand Developer OAuth scopes to full platform access"
```

---

## Task 6: Add Frontend Social Login API Functions

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Test: Verified by TypeScript compilation

**Step 1: Add social login functions to `frontend/src/lib/api.ts`**

Add after the existing `getMe` function (after line 68):

```typescript
// Social Login
export function getTikTokLoginUrl(): Promise<{ authorize_url: string }> {
  return apiFetch("/auth/tiktok/login");
}

export function getGoogleLoginUrl(): Promise<{ authorize_url: string }> {
  return apiFetch("/auth/google/login");
}

export function socialCallback(
  provider: "tiktok" | "google",
  code: string,
  state?: string
): Promise<TokenResponse> {
  const params = new URLSearchParams({ code });
  if (state) params.set("state", state);
  return apiFetch(`/auth/${provider}/callback?${params}`);
}
```

**Step 2: Verify TypeScript compiles**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo/frontend" && npx tsc --noEmit --pretty 2>&1 | head -20`
Expected: No new errors related to api.ts

**Step 3: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add social login API functions (TikTok, Google)"
```

---

## Task 7: Redesign Login Page with Social Login Buttons

**Files:**
- Modify: `frontend/src/app/(auth)/login/page.tsx`

**Step 1: Redesign the login page**

Replace entire file with a page that includes:
- "Continue with TikTok" button (black, TikTok branding)
- "Continue with Google" button (white, Google branding)
- Divider "or"
- Email/password form (existing)
- Link to register

The TikTok/Google buttons call `getTikTokLoginUrl()` / `getGoogleLoginUrl()` and then `window.location.href = url` to redirect to the OAuth provider.

```tsx
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { getTikTokLoginUrl, getGoogleLoginUrl, login } from "@/lib/api";
import { setTokens } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<string | null>(null);

  async function handleSocialLogin(provider: "tiktok" | "google") {
    setSocialLoading(provider);
    setError("");
    try {
      const fetcher = provider === "tiktok" ? getTikTokLoginUrl : getGoogleLoginUrl;
      const { authorize_url } = await fetcher();
      window.location.href = authorize_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : `${provider} login failed`);
      setSocialLoading(null);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const tokens = await login({ email, password });
      setTokens(tokens.access_token, tokens.refresh_token);
      router.push("/overview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950">
      <div className="max-w-md w-full space-y-6 p-8 bg-zinc-900 rounded-2xl border border-zinc-800">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">Frodo</h1>
          <p className="mt-1 text-sm text-zinc-400">One platform to rule them all</p>
        </div>

        {error && (
          <div className="bg-red-950/50 border border-red-800 text-red-300 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="space-y-3">
          <button
            onClick={() => handleSocialLogin("tiktok")}
            disabled={socialLoading !== null}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-black border border-zinc-700 rounded-lg text-white font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50"
          >
            {socialLoading === "tiktok" ? "Redirecting..." : "Continue with TikTok"}
          </button>

          <button
            onClick={() => handleSocialLogin("google")}
            disabled={socialLoading !== null}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-white border border-zinc-200 rounded-lg text-zinc-900 font-medium hover:bg-zinc-50 transition-colors disabled:opacity-50"
          >
            {socialLoading === "google" ? "Redirecting..." : "Continue with Google"}
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 h-px bg-zinc-800" />
          <span className="text-xs text-zinc-500 uppercase tracking-wider">or</span>
          <div className="flex-1 h-px bg-zinc-800" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-zinc-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-zinc-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in with email"}
          </button>
        </form>

        <p className="text-center text-sm text-zinc-500">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-blue-400 hover:text-blue-300">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/\(auth\)/login/page.tsx
git commit -m "feat: redesign login page with TikTok/Google social login"
```

---

## Task 8: Add Social Login Callback Page

**Files:**
- Create: `frontend/src/app/(auth)/callback/page.tsx`

**Step 1: Create callback page that handles OAuth redirect**

```tsx
// frontend/src/app/(auth)/callback/page.tsx
"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

import { socialCallback } from "@/lib/api";
import { setTokens } from "@/lib/auth";

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    // Determine provider from the referrer or state
    // The backend callback URLs redirect here with ?provider=tiktok|google&code=...
    const provider = searchParams.get("provider") as "tiktok" | "google" | null;

    if (!code || !provider) {
      setError("Invalid callback — missing code or provider");
      return;
    }

    socialCallback(provider, code, state || undefined)
      .then((tokens) => {
        setTokens(tokens.access_token, tokens.refresh_token);
        router.push("/overview");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Login failed");
      });
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="max-w-md w-full p-8 bg-zinc-900 rounded-2xl border border-zinc-800 text-center">
          <h1 className="text-xl font-bold text-red-400">Login Failed</h1>
          <p className="mt-2 text-sm text-zinc-400">{error}</p>
          <a href="/login" className="mt-4 inline-block text-blue-400 hover:text-blue-300">
            Back to login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto" />
        <p className="mt-4 text-zinc-400">Completing login...</p>
      </div>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-zinc-950">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white" />
        </div>
      }
    >
      <CallbackHandler />
    </Suspense>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/\(auth\)/callback/page.tsx
git commit -m "feat: add social login callback page"
```

---

## Task 9: Redesign Register Page with Social Options

**Files:**
- Modify: `frontend/src/app/(auth)/register/page.tsx`

**Step 1: Update register page to match new login design**

Same pattern as login — social buttons at top, then email/password form. Keep the organization name field. Dark theme matching login.

**Step 2: Commit**

```bash
git add frontend/src/app/\(auth\)/register/page.tsx
git commit -m "feat: redesign register page with social login options"
```

---

## Task 10: Add Alembic Migration for SocialIdentity + User.hashed_password Nullable

**Files:**
- Create: Alembic migration (auto-generated)

**Step 1: Generate migration**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && alembic revision --autogenerate -m "add social_identities table and make user password nullable"`

**Step 2: Review the generated migration**

Verify it creates `social_identities` table and alters `users.hashed_password` to nullable.

**Step 3: Apply migration**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && alembic upgrade head`

**Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: migration — add social_identities, nullable user password"
```

---

## Task 11: Run Full Test Suite — Regression Check

**Step 1: Run all tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/ -v --tb=short`
Expected: All 550+ existing tests PASS + new tests PASS

**Step 2: Fix any regressions**

If tests fail due to `hashed_password` now being nullable, update test fixtures that create User objects to explicitly set `hashed_password`.

**Step 3: Commit fixes if needed**

```bash
git add -A
git commit -m "fix: update test fixtures for nullable hashed_password"
```

---

## Task 12: Verify Frontend Build

**Step 1: Check TypeScript compilation**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo/frontend" && npx tsc --noEmit`
Expected: No errors

**Step 2: Check Next.js build**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo/frontend" && npx next build`
Expected: Build succeeds

**Step 3: Commit any fixes**

---

## Summary

After completing all 12 tasks, the auth system will support:

| Login Method | Status |
|-------------|--------|
| Email/password | Existing (unchanged) |
| Continue with TikTok | **NEW** |
| Continue with Google | **NEW** |

And the Connect pipeline will have:
- Full production OAuth scopes for Developer platform
- Foundation for further scope expansion (Shop/Marketing scopes are already broad)

**Next plan**: Phase 1 — Commerce Deep-Dive (separate plan doc targeting `knowledge-base/api-reference/` gaps)
