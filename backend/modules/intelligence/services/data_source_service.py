"""Data source aggregator service - manages data source configurations."""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.intelligence import ResearchQuery

logger = logging.getLogger(__name__)


# DataSourceConfig is stored as a ResearchQuery with a convention:
# name starts with "datasource:" and query_params holds config.
_DATASOURCE_PREFIX = "datasource:"


class DataSourceService:
    """Manages data source configurations using the aggregator pattern."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register_source(
        self,
        workspace_id: uuid.UUID,
        source_config: dict[str, Any],
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Register a data source configuration.

        source_config should contain:
        - name: human-readable source name
        - source_type: e.g. "tiktok_research", "tiktok_marketing"
        - enabled: bool (default True)
        - settings: dict of source-specific settings
        """
        source_name = source_config.get("name", "Unnamed Source")
        query = ResearchQuery(
            workspace_id=workspace_id,
            name=f"{_DATASOURCE_PREFIX}{source_name}",
            query_params={
                "source_type": source_config.get("source_type", "unknown"),
                "enabled": source_config.get("enabled", True),
                "settings": source_config.get("settings", {}),
            },
            created_by=user_id,
        )
        self._session.add(query)
        await self._session.flush()

        logger.info(
            "Registered data source '%s' for workspace %s",
            source_name,
            workspace_id,
        )
        return _serialize_source(query)

    async def list_sources(
        self,
        workspace_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """List all data source configs for a workspace."""
        result = await self._session.execute(
            select(ResearchQuery)
            .where(
                ResearchQuery.workspace_id == workspace_id,
                ResearchQuery.name.startswith(_DATASOURCE_PREFIX),
            )
            .order_by(ResearchQuery.created_at.desc())
        )
        sources = result.scalars().all()
        return [_serialize_source(s) for s in sources]

    async def toggle_source(
        self,
        workspace_id: uuid.UUID,
        source_id: uuid.UUID,
        enabled: bool,
    ) -> dict[str, Any] | None:
        """Enable or disable a data source. Returns updated source or None."""
        result = await self._session.execute(
            select(ResearchQuery).where(
                ResearchQuery.id == source_id,
                ResearchQuery.workspace_id == workspace_id,
                ResearchQuery.name.startswith(_DATASOURCE_PREFIX),
            )
        )
        source = result.scalar_one_or_none()
        if not source:
            return None

        params = dict(source.query_params) if source.query_params else {}
        params["enabled"] = enabled
        source.query_params = params
        await self._session.flush()

        logger.info("Toggled data source %s to enabled=%s", source_id, enabled)
        return _serialize_source(source)


def _serialize_source(query: ResearchQuery) -> dict[str, Any]:
    """Convert a ResearchQuery acting as DataSource to a response dict."""
    params = query.query_params or {}
    display_name = query.name
    if display_name.startswith(_DATASOURCE_PREFIX):
        display_name = display_name[len(_DATASOURCE_PREFIX) :]

    return {
        "id": str(query.id),
        "name": display_name,
        "source_type": params.get("source_type", "unknown"),
        "enabled": params.get("enabled", True),
        "settings": params.get("settings", {}),
        "created_at": (
            query.created_at.isoformat()
            if hasattr(query, "created_at") and query.created_at
            else None
        ),
    }
