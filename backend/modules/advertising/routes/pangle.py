from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.pangle_service import PangleService

router = APIRouter()


class UpdateBlockListRequest(BaseModel):
    ad_account_id: str
    block_list: list[str]
    action: str  # "ADD" or "REMOVE"


@router.get("/pangle/block-list")
async def get_block_list(
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = PangleService(db)
    return await service.get_block_list(ad_account, page=page, page_size=page_size)


@router.post("/pangle/block-list")
async def update_block_list(
    body: UpdateBlockListRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = PangleService(db)
    return await service.update_block_list(
        ad_account, block_list=body.block_list, action=body.action
    )


@router.get("/pangle/audience-packages")
async def get_audience_packages(
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = PangleService(db)
    return await service.get_audience_packages(
        ad_account, page=page, page_size=page_size
    )
