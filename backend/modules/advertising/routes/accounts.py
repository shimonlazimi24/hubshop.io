import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import AdAccountResponse
from backend.modules.advertising.services.ad_account_service import AdAccountService

router = APIRouter()


@router.get("/accounts", response_model=list[AdAccountResponse])
async def list_ad_accounts(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[AdAccountResponse]:
    service = AdAccountService(db)
    accounts = await service.list_ad_accounts(workspace_id)
    return [AdAccountResponse.model_validate(a) for a in accounts]


@router.get("/accounts/{ad_account_id}", response_model=AdAccountResponse)
async def get_ad_account(
    ad_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> AdAccountResponse:
    service = AdAccountService(db)
    account = await service.get_ad_account(ad_account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )
    return AdAccountResponse.model_validate(account)


@router.post("/accounts/sync")
async def sync_ad_accounts(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = AdAccountService(db)
    synced = await service.sync_ad_accounts_from_connected(workspace_id)
    return {"synced": len(synced)}
