import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.shop_health import HealthAlert

logger = logging.getLogger(__name__)

ALERT_THRESHOLDS: list[dict] = [
    {
        "metric": "estimated_score",
        "op": "lt",
        "value": 3.0,
        "severity": "CRITICAL",
        "type": "SPS_DROP",
        "message": "Shop health degrading — review returns and CS response time",
    },
    {
        "metric": "estimated_score",
        "op": "lt",
        "value": 3.5,
        "severity": "WARNING",
        "type": "SPS_DROP",
        "message": "Settlement tier at risk — will drop from Accelerated to Standard",
    },
    {
        "metric": "violation_points",
        "op": "gte",
        "value": 24,
        "severity": "CRITICAL",
        "type": "VIOLATION_THRESHOLD",
        "message": "Livestream traffic reduction + new listing block imminent",
    },
    {
        "metric": "violation_points",
        "op": "gte",
        "value": 12,
        "severity": "WARNING",
        "type": "VIOLATION_THRESHOLD",
        "message": "Losing campaign access at 12 points",
    },
    {
        "metric": "cs_response_rate",
        "op": "lt",
        "value": 85.0,
        "severity": "WARNING",
        "type": "CS_DEGRADATION",
        "message": "Approaching 80% threshold — IM dissatisfaction will increase",
    },
    {
        "metric": "otdr",
        "op": "lt",
        "value": 90.0,
        "severity": "WARNING",
        "type": "OTDR_WARNING",
        "message": "On-time delivery rate degrading — check fulfillment pipeline",
    },
]


def _check_threshold(metric_value: float, op: str, threshold_value: float) -> bool:
    """Check if a metric value triggers the given comparison operator."""
    if op == "lt":
        return metric_value < threshold_value
    if op == "gte":
        return metric_value >= threshold_value
    if op == "lte":
        return metric_value <= threshold_value
    if op == "gt":
        return metric_value > threshold_value
    return False


class AlertService:
    """Evaluate shop health metrics against thresholds and manage alerts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def evaluate_and_create_alerts(
        self,
        workspace_id: uuid.UUID,
        shop_id: uuid.UUID,
        metrics: dict,
    ) -> list[HealthAlert]:
        """Evaluate metrics against thresholds and create alerts for breaches.

        To avoid duplicate alerts from a single threshold (e.g. estimated_score=2.5
        triggers both the <3.5 WARNING and the <3.0 CRITICAL), we track which
        (alert_type, severity) combinations have already fired and skip the
        lower-severity duplicate for the same type.
        """
        now = datetime.now(tz=UTC)
        alerts: list[HealthAlert] = []
        # Track which (type, severity) we've already created to avoid redundancy.
        # CRITICAL thresholds are listed before WARNING for the same type,
        # so if CRITICAL fires we skip the WARNING of the same type.
        fired: set[tuple[str, str]] = set()

        for threshold in ALERT_THRESHOLDS:
            metric_name = threshold["metric"]
            metric_value = metrics.get(metric_name)
            if metric_value is None:
                continue

            alert_type = threshold["type"]
            severity = threshold["severity"]

            # If we already fired a CRITICAL for this type, skip the WARNING
            if severity == "WARNING" and (alert_type, "CRITICAL") in fired:
                continue

            if _check_threshold(
                float(metric_value), threshold["op"], threshold["value"]
            ):
                alert = HealthAlert(
                    workspace_id=workspace_id,
                    shop_id=shop_id,
                    alert_type=alert_type,
                    severity=severity,
                    message=threshold["message"],
                    metric_name=metric_name,
                    current_value=str(metric_value),
                    threshold_value=str(threshold["value"]),
                    triggered_at=now,
                )
                self._session.add(alert)
                alerts.append(alert)
                fired.add((alert_type, severity))

        return alerts

    async def list_alerts(
        self,
        workspace_id: uuid.UUID,
        severity: str | None = None,
        acknowledged: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List alerts with optional filtering and pagination."""
        base_where = [HealthAlert.workspace_id == workspace_id]

        if severity is not None:
            base_where.append(HealthAlert.severity == severity)
        if acknowledged is True:
            base_where.append(HealthAlert.acknowledged_at.isnot(None))
        elif acknowledged is False:
            base_where.append(HealthAlert.acknowledged_at.is_(None))

        # Count total
        count_stmt = select(func.count(HealthAlert.id)).where(*base_where)
        total = (await self._session.execute(count_stmt)).scalar_one()

        # Fetch page
        offset = (page - 1) * page_size
        items_stmt = (
            select(HealthAlert)
            .where(*base_where)
            .order_by(HealthAlert.triggered_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = (await self._session.execute(items_stmt)).scalars().all()

        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def acknowledge_alert(self, alert_id: uuid.UUID) -> HealthAlert:
        """Mark an alert as acknowledged."""
        result = await self._session.execute(
            select(HealthAlert).where(HealthAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if alert is None:
            raise ValueError(f"Alert not found: {alert_id}")

        alert.acknowledged_at = datetime.now(tz=UTC)
        return alert
