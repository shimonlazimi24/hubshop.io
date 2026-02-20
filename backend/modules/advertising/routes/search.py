import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.search_keyword_service import (
    SearchKeywordService,
)

router = APIRouter()


class CreateNegativeKeywordRequest(BaseModel):
    ad_account_id: str
    ad_group_id: str
    keyword: str
    match_type: str = "EXACT"


class UpdateNegativeKeywordRequest(BaseModel):
    ad_account_id: str
    updates: dict


class DeleteNegativeKeywordRequest(BaseModel):
    ad_account_id: str
    keyword_ids: list[str]


@router.get("/search/keywords/recommend")
async def recommend_keywords(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    keyword: str,
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

    service = SearchKeywordService(db)
    return await service.recommend_keywords(
        workspace_id, ad_account, keyword=keyword, page=page, page_size=page_size
    )


@router.get("/search/keywords/discover")
async def discover_keywords(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    keyword: str,
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

    service = SearchKeywordService(db)
    return await service.discover_keywords(
        workspace_id, ad_account, keyword=keyword, page=page, page_size=page_size
    )


@router.get("/search/negative-keywords")
async def list_negative_keywords(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_group_id: str,
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

    service = SearchKeywordService(db)
    return await service.list_negative_keywords(
        workspace_id,
        ad_account,
        ad_group_id=ad_group_id,
        page=page,
        page_size=page_size,
    )


@router.post("/search/negative-keywords")
async def create_negative_keyword(
    workspace_id: uuid.UUID,
    body: CreateNegativeKeywordRequest,
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

    service = SearchKeywordService(db)
    return await service.create_negative_keyword(
        workspace_id,
        ad_account,
        ad_group_id=body.ad_group_id,
        keyword=body.keyword,
        match_type=body.match_type,
    )


@router.post("/search/negative-keywords/{keyword_id}")
async def update_negative_keyword(
    workspace_id: uuid.UUID,
    keyword_id: str,
    body: UpdateNegativeKeywordRequest,
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

    service = SearchKeywordService(db)
    return await service.update_negative_keyword(
        workspace_id, ad_account, keyword_id=keyword_id, updates=body.updates
    )


@router.delete("/search/negative-keywords")
async def delete_negative_keywords(
    workspace_id: uuid.UUID,
    body: DeleteNegativeKeywordRequest,
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

    service = SearchKeywordService(db)
    return await service.delete_negative_keyword(
        workspace_id, ad_account, keyword_ids=body.keyword_ids
    )
