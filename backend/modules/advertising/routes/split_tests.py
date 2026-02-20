import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.split_test_service import SplitTestService

router = APIRouter()


class CreateSplitTestRequest(BaseModel):
    ad_account_id: str
    test_config: dict


class UpdateTestTimeRequest(BaseModel):
    ad_account_id: str
    updates: dict


class EndSplitTestRequest(BaseModel):
    ad_account_id: str


class ApplyWinnerRequest(BaseModel):
    ad_account_id: str


@router.get("/split-tests/{split_test_id}/results")
async def get_results(
    workspace_id: uuid.UUID,
    split_test_id: str,
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

    service = SplitTestService(db)
    return await service.get_results(
        workspace_id, ad_account, split_test_id=split_test_id
    )


@router.post("/split-tests")
async def create_split_test(
    workspace_id: uuid.UUID,
    body: CreateSplitTestRequest,
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

    service = SplitTestService(db)
    return await service.create_split_test(
        workspace_id, ad_account, test_config=body.test_config
    )


@router.post("/split-tests/{split_test_id}/time")
async def update_test_time(
    workspace_id: uuid.UUID,
    split_test_id: str,
    body: UpdateTestTimeRequest,
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

    service = SplitTestService(db)
    return await service.update_test_time(
        workspace_id,
        ad_account,
        split_test_id=split_test_id,
        updates=body.updates,
    )


@router.post("/split-tests/{split_test_id}/end")
async def end_split_test(
    workspace_id: uuid.UUID,
    split_test_id: str,
    body: EndSplitTestRequest,
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

    service = SplitTestService(db)
    return await service.end_split_test(
        workspace_id, ad_account, split_test_id=split_test_id
    )


@router.post("/split-tests/{split_test_id}/winner")
async def apply_winner(
    workspace_id: uuid.UUID,
    split_test_id: str,
    body: ApplyWinnerRequest,
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

    service = SplitTestService(db)
    return await service.apply_winner(
        workspace_id, ad_account, split_test_id=split_test_id
    )
