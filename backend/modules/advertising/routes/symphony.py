import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.symphony_service import SymphonyService

router = APIRouter()


class CreateSmartCreativeAdRequest(BaseModel):
    ad_account_id: str
    ad_config: dict


class UpdateSmartCreativeMaterialsRequest(BaseModel):
    ad_account_id: str
    ad_id: str
    materials: list[dict]


class CreateSmartFixRequest(BaseModel):
    ad_account_id: str
    creative_id: str


@router.get("/symphony/smart-creative/materials")
async def get_smart_creative_materials(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = SymphonyService(db)
    return await service.get_smart_creative_materials(
        workspace_id, ad_account, ad_id
    )


@router.post("/symphony/smart-creative/ads")
async def create_smart_creative_ad(
    workspace_id: uuid.UUID,
    body: CreateSmartCreativeAdRequest,
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

    service = SymphonyService(db)
    return await service.create_smart_creative_ad(
        workspace_id, ad_account, ad_config=body.ad_config
    )


@router.post("/symphony/smart-creative/materials")
async def update_smart_creative_materials(
    workspace_id: uuid.UUID,
    body: UpdateSmartCreativeMaterialsRequest,
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

    service = SymphonyService(db)
    return await service.update_smart_creative_materials(
        workspace_id, ad_account, ad_id=body.ad_id, materials=body.materials
    )


@router.get("/symphony/smart-text/recommend")
async def recommend_smart_text(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_text: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = SymphonyService(db)
    return await service.recommend_smart_text(workspace_id, ad_account, ad_text)


@router.get("/symphony/cta/recommend")
async def recommend_cta(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    objective: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = SymphonyService(db)
    return await service.recommend_cta(workspace_id, ad_account, objective)


@router.post("/symphony/smart-fix")
async def create_smart_fix(
    workspace_id: uuid.UUID,
    body: CreateSmartFixRequest,
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

    service = SymphonyService(db)
    return await service.create_smart_fix(
        workspace_id, ad_account, creative_id=body.creative_id
    )


@router.get("/symphony/smart-fix/{task_id}")
async def get_smart_fix_result(
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

    service = SymphonyService(db)
    return await service.get_smart_fix_result(workspace_id, ad_account, task_id)


@router.get("/symphony/fatigue/detect")
async def detect_fatigue(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_ids: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    ad_id_list = [aid.strip() for aid in ad_ids.split(",") if aid.strip()]
    service = SymphonyService(db)
    return await service.detect_fatigue(workspace_id, ad_account, ad_id_list)
