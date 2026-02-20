import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.creative_service import CreativeService

router = APIRouter()


class CreatePortfolioRequest(BaseModel):
    ad_account_id: str
    name: str


class SmartTextRequest(BaseModel):
    ad_account_id: str
    params: dict


@router.get("/creatives/portfolios")
async def list_portfolios(
    workspace_id: uuid.UUID,
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = CreativeService(db)
    return await service.list_portfolios(
        workspace_id, ad_account, page=page, page_size=page_size
    )


@router.post("/creatives/portfolios")
async def create_portfolio(
    workspace_id: uuid.UUID,
    body: CreatePortfolioRequest,
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

    service = CreativeService(db)
    return await service.create_portfolio(workspace_id, ad_account, name=body.name)


@router.post("/creatives/smart-text")
async def generate_smart_text(
    workspace_id: uuid.UUID,
    body: SmartTextRequest,
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

    service = CreativeService(db)
    return await service.generate_smart_text(
        workspace_id, ad_account, params=body.params
    )


@router.get("/creatives/trending-hashtags")
async def get_trending_hashtags(
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

    service = CreativeService(db)
    return await service.get_trending_hashtags(workspace_id, ad_account)
