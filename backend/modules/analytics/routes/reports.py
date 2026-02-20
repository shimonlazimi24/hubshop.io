import uuid

from fastapi import APIRouter, HTTPException

from backend.dependencies import CurrentUser, DBSession
from backend.modules.analytics.schemas import (
    CreateReportRequest,
    ScheduledReportResponse,
    UpdateReportRequest,
)
from backend.modules.analytics.services.report_service import ReportService

router = APIRouter()


@router.get("/reports")
async def list_reports(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    is_active: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List scheduled reports."""
    service = ReportService(db)
    result = await service.list_reports(
        workspace_id, is_active=is_active, page=page, page_size=page_size
    )
    return {
        "items": [ScheduledReportResponse.model_validate(r) for r in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "total_pages": result.total_pages,
    }


@router.post("/reports", status_code=201)
async def create_report(
    workspace_id: uuid.UUID,
    body: CreateReportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ScheduledReportResponse:
    """Create a scheduled report."""
    service = ReportService(db)
    report = await service.create_report(
        workspace_id,
        current_user.id,
        name=body.name,
        description=body.description,
        modules=body.modules,
        metrics=body.metrics,
        frequency=body.frequency,
        format=body.format,
    )
    await db.commit()
    return ScheduledReportResponse.model_validate(report)


@router.get("/reports/{report_id}")
async def get_report(
    report_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ScheduledReportResponse:
    """Get a single report."""
    service = ReportService(db)
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ScheduledReportResponse.model_validate(report)


@router.put("/reports/{report_id}")
async def update_report(
    report_id: uuid.UUID,
    body: UpdateReportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ScheduledReportResponse:
    """Update a scheduled report."""
    service = ReportService(db)
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    updated = await service.update_report(
        report,
        name=body.name,
        description=body.description,
        modules=body.modules,
        frequency=body.frequency,
        format=body.format,
        is_active=body.is_active,
    )
    await db.commit()
    return ScheduledReportResponse.model_validate(updated)


@router.delete("/reports/{report_id}", status_code=204)
async def delete_report(
    report_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Delete a scheduled report."""
    service = ReportService(db)
    deleted = await service.delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    await db.commit()


@router.post("/reports/{report_id}/generate")
async def generate_report(
    report_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Generate a report now."""
    service = ReportService(db)
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    result = await service.generate_report(report)
    await db.commit()
    return result
