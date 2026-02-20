import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.custom_conversion_service import (
    CustomConversionService,
)

router = APIRouter()


class CreateConversionRequest(BaseModel):
    ad_account_id: str
    conversion_config: dict


class UpdateConversionRequest(BaseModel):
    ad_account_id: str
    updates: dict


class DeleteConversionRequest(BaseModel):
    ad_account_id: str


@router.get("/custom-conversions")
async def list_conversions(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    pixel_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = CustomConversionService(db)
    return await service.list_conversions(
        workspace_id, ad_account, pixel_id=pixel_id
    )


@router.post("/custom-conversions")
async def create_conversion(
    workspace_id: uuid.UUID,
    body: CreateConversionRequest,
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

    service = CustomConversionService(db)
    return await service.create_conversion(
        workspace_id, ad_account, conversion_config=body.conversion_config
    )


@router.get("/custom-conversions/{custom_conversion_id}")
async def get_conversion_detail(
    workspace_id: uuid.UUID,
    custom_conversion_id: str,
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

    service = CustomConversionService(db)
    return await service.get_conversion_detail(
        workspace_id, ad_account, custom_conversion_id=custom_conversion_id
    )


@router.post("/custom-conversions/{custom_conversion_id}")
async def update_conversion(
    workspace_id: uuid.UUID,
    custom_conversion_id: str,
    body: UpdateConversionRequest,
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

    service = CustomConversionService(db)
    return await service.update_conversion(
        workspace_id,
        ad_account,
        custom_conversion_id=custom_conversion_id,
        updates=body.updates,
    )


@router.delete("/custom-conversions/{custom_conversion_id}")
async def delete_conversion(
    workspace_id: uuid.UUID,
    custom_conversion_id: str,
    body: DeleteConversionRequest,
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

    service = CustomConversionService(db)
    return await service.delete_conversion(
        workspace_id, ad_account, custom_conversion_id=custom_conversion_id
    )
