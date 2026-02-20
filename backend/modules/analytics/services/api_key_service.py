import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.analytics import ApiKey

logger = logging.getLogger(__name__)


class ApiKeyService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_key(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        name: str,
        scopes: list[str] | None = None,
    ) -> tuple[ApiKey, str]:
        """Create a new API key. Returns (key_model, raw_key).

        The raw key is only available at creation time.
        """
        full_key, prefix, key_hash = ApiKey.generate_key()
        key = ApiKey(
            workspace_id=workspace_id,
            created_by=user_id,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            scopes=scopes or [],
            is_active=True,
        )
        self._session.add(key)
        await self._session.flush()
        return key, full_key

    async def list_keys(self, workspace_id: uuid.UUID) -> list[ApiKey]:
        result = await self._session.execute(
            select(ApiKey)
            .where(ApiKey.workspace_id == workspace_id)
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_key(
        self, key_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> ApiKey | None:
        result = await self._session.execute(
            select(ApiKey).where(
                ApiKey.id == key_id,
                ApiKey.workspace_id == workspace_id,
            )
        )
        key = result.scalar_one_or_none()
        if key:
            key.is_active = False
        return key

    async def validate_key(self, raw_key: str) -> ApiKey | None:
        """Validate an API key and update last_used_at."""
        key_hash = ApiKey.hash_key(raw_key)
        result = await self._session.execute(
            select(ApiKey).where(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active.is_(True),
            )
        )
        key = result.scalar_one_or_none()
        if not key:
            return None

        # Check expiry
        if key.expires_at and key.expires_at < datetime.now(tz=UTC):
            return None

        key.last_used_at = datetime.now(tz=UTC)
        return key
