import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.lead_service import LeadService

router = APIRouter()


class CreateTestLeadRequest(BaseModel):
    ad_account_id: str
    form_id: str
    lead_data: dict


class CreateDownloadTaskRequest(BaseModel):
    ad_account_id: str
    form_id: str
    start_date: str
    end_date: str


@router.get("/leads")
async def get_leads(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    form_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = LeadService(db)
    return await service.get_leads(
        workspace_id,
        ad_account,
        form_id=form_id,
        page=page,
        page_size=page_size,
    )


@router.post("/leads/test")
async def create_test_lead(
    workspace_id: uuid.UUID,
    body: CreateTestLeadRequest,
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

    service = LeadService(db)
    return await service.create_test_lead(
        workspace_id,
        ad_account,
        form_id=body.form_id,
        lead_data=body.lead_data,
    )


@router.get("/leads/test/{test_lead_id}")
async def get_test_lead(
    workspace_id: uuid.UUID,
    test_lead_id: str,
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

    service = LeadService(db)
    return await service.get_test_lead(
        workspace_id, ad_account, test_lead_id=test_lead_id
    )


@router.post("/leads/download")
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

    service = LeadService(db)
    return await service.create_download_task(
        workspace_id,
        ad_account,
        form_id=body.form_id,
        start_date=body.start_date,
        end_date=body.end_date,
    )


@router.get("/leads/download/{task_id}")
async def download_leads(
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

    service = LeadService(db)
    return await service.download_leads(workspace_id, ad_account, task_id=task_id)


@router.get("/leads/form/libraries")
async def get_form_libraries(
    workspace_id: uuid.UUID,
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

    service = LeadService(db)
    return await service.get_form_libraries(workspace_id, ad_account)


@router.get("/leads/form/{form_id}/fields")
async def get_form_fields(
    workspace_id: uuid.UUID,
    form_id: str,
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

    service = LeadService(db)
    return await service.get_form_fields(
        workspace_id, ad_account, form_id=form_id
    )
