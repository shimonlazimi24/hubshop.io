import uuid

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import UploadImageRequest, UploadVideoRequest
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


# --- Creative Upload & Management ---


@router.post("/creatives/videos/upload")
async def upload_video(
    workspace_id: uuid.UUID,
    body: UploadVideoRequest,
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
    return await service.upload_video(
        workspace_id,
        ad_account,
        video_url=body.video_url,
        video_name=body.video_name,
    )


@router.get("/creatives/videos/info")
async def get_video_info(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    video_ids: str = Query(..., description="Comma-separated video IDs"),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    ids_list = [vid.strip() for vid in video_ids.split(",") if vid.strip()]
    service = CreativeService(db)
    return await service.get_video_info(
        workspace_id, ad_account, video_ids=ids_list
    )


@router.post("/creatives/images/upload")
async def upload_image(
    workspace_id: uuid.UUID,
    body: UploadImageRequest,
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
    return await service.upload_image(
        workspace_id,
        ad_account,
        image_url=body.image_url,
        image_name=body.image_name,
    )


@router.get("/creatives/images/info")
async def get_image_info(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    image_ids: str = Query(..., description="Comma-separated image IDs"),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    ids_list = [iid.strip() for iid in image_ids.split(",") if iid.strip()]
    service = CreativeService(db)
    return await service.get_image_info(
        workspace_id, ad_account, image_ids=ids_list
    )


@router.get("/creatives/music/search")
async def search_music(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    query: str = Query(..., description="Music search query"),
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
    return await service.search_music(
        workspace_id,
        ad_account,
        query=query,
        page=page,
        page_size=page_size,
    )
