import uuid

from fastapi import APIRouter, Query

from backend.db.models.shop_health import ViolationRecord
from backend.dependencies import CurrentUser, DBSession, Pagination, WorkspaceId
from backend.modules.shop_health.schemas import (
    AcknowledgeAlertRequest,
    CreateViolationRequest,
    HealthAlertResponse,
    PaginatedAlertsResponse,
    SpsCurrentResponse,
    SpsSnapshotResponse,
    UnifiedMetricsResponse,
    ViolationResponse,
)
from backend.modules.shop_health.services.alert_service import AlertService
from backend.modules.shop_health.services.analytics_service import (
    UnifiedAnalyticsService,
)
from backend.modules.shop_health.services.sps_service import SpsEstimationService

router = APIRouter(prefix="/shop-health", tags=["shop-health"])


@router.get("/sps")
async def get_current_sps(
    workspace_id: WorkspaceId,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID = Query(...),
) -> SpsCurrentResponse:
    """Get current estimated SPS for a shop."""
    service = SpsEstimationService(db)
    metrics = await service.calculate_estimated_sps(workspace_id, shop_id)
    return SpsCurrentResponse(**metrics)


@router.get("/sps/history")
async def get_sps_history(
    workspace_id: WorkspaceId,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = Query(None),
    days: int = Query(30, ge=1, le=365),
) -> list[SpsSnapshotResponse]:
    """Get SPS snapshot history for trend analysis."""
    service = SpsEstimationService(db)
    snapshots = await service.get_sps_history(workspace_id, shop_id=shop_id, days=days)
    return [SpsSnapshotResponse.model_validate(s) for s in snapshots]


@router.get("/violations")
async def list_violations(
    workspace_id: WorkspaceId,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = Query(None),
) -> list[ViolationResponse]:
    """List violation records for a workspace."""
    from sqlalchemy import select

    stmt = select(ViolationRecord).where(ViolationRecord.workspace_id == workspace_id)
    if shop_id is not None:
        stmt = stmt.where(ViolationRecord.shop_id == shop_id)
    stmt = stmt.order_by(ViolationRecord.occurred_at.desc())
    result = await db.execute(stmt)
    violations = result.scalars().all()
    return [ViolationResponse.model_validate(v) for v in violations]


@router.post("/violations", status_code=201)
async def create_violation(
    workspace_id: WorkspaceId,
    current_user: CurrentUser,
    db: DBSession,
    request: CreateViolationRequest,
) -> ViolationResponse:
    """Manually record a policy violation."""
    violation = ViolationRecord(
        workspace_id=workspace_id,
        shop_id=uuid.UUID(request.shop_id),
        violation_type=request.violation_type,
        points=request.points,
        description=request.description,
        occurred_at=request.occurred_at,
        expires_at=request.expires_at,
        source="MANUAL",
    )
    db.add(violation)
    await db.flush()
    return ViolationResponse.model_validate(violation)


@router.get("/alerts")
async def list_alerts(
    workspace_id: WorkspaceId,
    current_user: CurrentUser,
    db: DBSession,
    pagination: Pagination,
    severity: str | None = Query(None),
    acknowledged: bool | None = Query(None),
) -> PaginatedAlertsResponse:
    """List health alerts with optional filtering."""
    page, page_size = pagination
    service = AlertService(db)
    result = await service.list_alerts(
        workspace_id,
        severity=severity,
        acknowledged=acknowledged,
        page=page,
        page_size=page_size,
    )
    return PaginatedAlertsResponse(
        items=[HealthAlertResponse.model_validate(a) for a in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> HealthAlertResponse:
    """Acknowledge a health alert."""
    service = AlertService(db)
    alert = await service.acknowledge_alert(alert_id)
    return HealthAlertResponse.model_validate(alert)


@router.get("/analytics")
async def get_analytics(
    workspace_id: WorkspaceId,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = Query(None),
    days: int = Query(30, ge=1, le=365),
) -> list[UnifiedMetricsResponse]:
    """Get unified daily analytics metrics."""
    service = UnifiedAnalyticsService(db)
    metrics = await service.get_metrics_history(
        workspace_id, shop_id=shop_id, days=days
    )
    return [UnifiedMetricsResponse.model_validate(m) for m in metrics]
