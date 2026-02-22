import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.content.schemas import (
    AdReportRequest,
    SearchAdsRequest,
    SearchAdvertisersRequest,
    SearchCommercialContentRequest,
)
from backend.modules.content.services.commercial_content_service import (
    CommercialContentService,
)

router = APIRouter()


@router.post("/commercial/ads/search")
async def search_ads(
    workspace_id: uuid.UUID,
    body: SearchAdsRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CommercialContentService(db)
    return await service.search_ads(
        workspace_id,
        search_term=body.search_term,
        date_range=body.date_range,
        country_code=body.country_code,
        advertiser_business_ids=body.advertiser_business_ids,
        max_count=body.max_count,
        search_id=body.search_id,
    )


@router.post("/commercial/advertisers/search")
async def search_advertisers(
    workspace_id: uuid.UUID,
    body: SearchAdvertisersRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CommercialContentService(db)
    return await service.search_advertisers(
        workspace_id,
        search_term=body.search_term,
        max_count=body.max_count,
    )


@router.post("/commercial/ads/{ad_id}/detail")
async def get_ad_detail(
    workspace_id: uuid.UUID,
    ad_id: int,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CommercialContentService(db)
    return await service.get_ad_detail(workspace_id, ad_id=ad_id)


@router.post("/commercial/ads/report")
async def get_ad_report(
    workspace_id: uuid.UUID,
    body: AdReportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CommercialContentService(db)
    return await service.get_ad_report(
        workspace_id,
        date_range=body.date_range,
        country_code=body.country_code,
        advertiser_business_ids=body.advertiser_business_ids,
    )


@router.post("/commercial/content/search")
async def search_commercial_content(
    workspace_id: uuid.UUID,
    body: SearchCommercialContentRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CommercialContentService(db)
    return await service.search_commercial_content(
        workspace_id,
        date_range=body.date_range,
        creator_usernames=body.creator_usernames,
        creator_country_code=body.creator_country_code,
        max_count=body.max_count,
        search_id=body.search_id,
    )
