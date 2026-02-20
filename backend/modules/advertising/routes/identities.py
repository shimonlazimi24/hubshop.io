import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.identity_service import IdentityService

router = APIRouter()


class CreateIdentityRequest(BaseModel):
    ad_account_id: str
    identity_config: dict


class DeleteIdentityRequest(BaseModel):
    ad_account_id: str


@router.get("/identities")
async def list_identities(
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

    service = IdentityService(db)
    return await service.list_identities(
        workspace_id, ad_account, page=page, page_size=page_size
    )


@router.post("/identities")
async def create_identity(
    workspace_id: uuid.UUID,
    body: CreateIdentityRequest,
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

    service = IdentityService(db)
    return await service.create_identity(
        workspace_id, ad_account, identity_config=body.identity_config
    )


@router.get("/identities/{identity_id}")
async def get_identity_detail(
    workspace_id: uuid.UUID,
    identity_id: str,
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

    service = IdentityService(db)
    return await service.get_identity_detail(
        workspace_id, ad_account, identity_id=identity_id
    )


@router.get("/identities/{identity_id}/posts")
async def get_identity_posts(
    workspace_id: uuid.UUID,
    identity_id: str,
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

    service = IdentityService(db)
    return await service.get_identity_posts(
        workspace_id, ad_account, identity_id=identity_id
    )


@router.delete("/identities/{identity_id}")
async def delete_identity(
    workspace_id: uuid.UUID,
    identity_id: str,
    body: DeleteIdentityRequest,
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

    service = IdentityService(db)
    return await service.delete_identity(
        workspace_id, ad_account, identity_id=identity_id
    )
