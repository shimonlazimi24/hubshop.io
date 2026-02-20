"""Competitor tracking service - stub for Sub-Phase C implementation."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class CompetitorService:
    """Tracks and analyzes competitor content using Research API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def sync_all_competitors(
        self, workspace_id: UUID, research_client: Any
    ) -> None:
        """Sync all competitor content for a workspace. Implemented in Sub-Phase C."""
        raise NotImplementedError(
            "CompetitorService.sync_all_competitors not yet implemented"
        )
