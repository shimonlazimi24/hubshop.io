import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AsyncReportStatusResponse,
    AsyncReportTaskResponse,
    ReportRequest,
    ReportResponse,
    ReportRowResponse,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.report_service import ReportService

router = APIRouter()


@router.post("/reports/sync", response_model=ReportResponse)
async def get_sync_report(
    body: ReportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ReportResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = ReportService(db)
    report_data = await service.get_sync_report(
        ad_account,
        report_type=body.report_type,
        data_level=body.data_level,
        date_start=body.date_start,
        date_end=body.date_end,
        metrics=body.metrics or None,
        dimensions=body.dimensions or None,
    )

    rows = [
        ReportRowResponse(
            dimensions=row.get("dimensions", {}),
            metrics=row.get("metrics", {}),
        )
        for row in report_data.get("rows", [])
    ]
    return ReportResponse(rows=rows, total_rows=len(rows))


@router.post("/reports/async", response_model=AsyncReportTaskResponse)
async def create_async_report(
    body: ReportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AsyncReportTaskResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = ReportService(db)
    task_id = await service.create_async_report(
        ad_account,
        report_type=body.report_type,
        data_level=body.data_level,
        date_start=body.date_start,
        date_end=body.date_end,
        metrics=body.metrics or None,
        dimensions=body.dimensions or None,
    )
    return AsyncReportTaskResponse(task_id=task_id)


@router.get(
    "/reports/async/{task_id}",
    response_model=AsyncReportStatusResponse,
)
async def check_async_report(
    task_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> AsyncReportStatusResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = ReportService(db)
    result = await service.check_async_report(ad_account, task_id)
    return AsyncReportStatusResponse(**result)


@router.get("/reports/async/{task_id}/download")
async def download_async_report(
    task_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = ReportService(db)
    return await service.download_async_report(ad_account, task_id)


@router.post("/reports/async/{task_id}/cancel")
async def cancel_async_report(
    task_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = ReportService(db)
    return await service.cancel_async_report(ad_account, task_id)


class GmvMaxReportRequest(BaseModel):
    ad_account_id: str
    date_start: str
    date_end: str
    metrics: list[str] = []
    dimensions: list[str] = []
    campaign_ids: list[str] = []


@router.post("/reports/gmv-max", response_model=ReportResponse)
async def get_gmv_max_report(
    body: GmvMaxReportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ReportResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = ReportService(db)
    report_data = await service.get_gmv_max_report(
        ad_account,
        date_start=body.date_start,
        date_end=body.date_end,
        metrics=body.metrics or None,
        dimensions=body.dimensions or None,
        campaign_ids=body.campaign_ids or None,
    )

    rows = [
        ReportRowResponse(
            dimensions=row.get("dimensions", {}),
            metrics=row.get("metrics", {}),
        )
        for row in report_data.get("rows", [])
    ]
    return ReportResponse(rows=rows, total_rows=len(rows))
