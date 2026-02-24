import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.change_log_service import ChangeLogService

router = APIRouter()


class CreateDownloadTaskRequest(BaseModel):
    ad_account_id: str
    object_type: str
    start_date: str
    end_date: str


@router.get("/change-log/tasks/{task_id}/status")
async def get_task_status(
    workspace_id: uuid.UUID,
    task_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = ChangeLogService(db)
    return await service.get_task_status(workspace_id, ad_account, task_id=task_id)


@router.get("/change-log/tasks/{task_id}/download")
async def download_file(
    workspace_id: uuid.UUID,
    task_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = ChangeLogService(db)
    return await service.download_file(workspace_id, ad_account, task_id=task_id)


@router.post("/change-log/tasks")
async def create_download_task(
    workspace_id: uuid.UUID,
    body: CreateDownloadTaskRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = ChangeLogService(db)
    return await service.create_download_task(
        workspace_id,
        ad_account,
        object_type=body.object_type,
        start_date=body.start_date,
        end_date=body.end_date,
    )
