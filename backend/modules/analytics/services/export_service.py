import csv
import io
import json
import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.analytics.services.unified_analytics_service import (
    UnifiedAnalyticsService,
)

logger = logging.getLogger(__name__)


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def export_data(
        self,
        workspace_id: uuid.UUID,
        *,
        dataset: str,
        format: str = "json",
        days: int = 30,
    ) -> dict:
        """Export a dataset as JSON or CSV string."""
        analytics = UnifiedAnalyticsService(self._session)

        if dataset == "overview":
            data = await analytics.get_overview_kpis(workspace_id, days=days)
            rows = [data]
        elif dataset == "revenue":
            rows = await analytics.get_revenue_vs_spend(workspace_id, days=days)
        elif dataset == "content":
            rows = await analytics.get_content_performance(workspace_id)
        elif dataset == "top_performers":
            data = await analytics.get_top_performers(workspace_id)
            rows = [data]
        else:
            raise ValueError(f"Unknown dataset: {dataset}")

        if format == "csv":
            return {"format": "csv", "content": self._to_csv(rows)}
        return {"format": "json", "content": json.dumps(rows, default=str)}

    def _to_csv(self, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
