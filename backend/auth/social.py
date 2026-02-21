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
        """Find existing user by social identity or create new one. Returns (user, is_new)."""
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

        # Check if user with this email exists (link identity)
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

        identity = SocialIdentity(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        self._db.add(identity)
        return user, is_new

    @staticmethod
    def _org_name_from_email(email: str) -> str:
        domain = email.split("@")[1] if "@" in email else email
        return domain.split(".")[0]

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
