from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.store_service import StoreService

router = APIRouter()


@router.get("/store")
async def list_stores(
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List stores linked to an advertiser account."""
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = StoreService(db)
    return await service.list_stores(ad_account, page=page, page_size=page_size)


@router.get("/store/{store_id}/products")
async def get_store_products(
    store_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List products within a specific store."""
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = StoreService(db)
    return await service.get_store_products(
        ad_account, store_id, page=page, page_size=page_size
    )


@router.get("/showcase/identities")
async def get_showcase_identities(
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get showcase identities for an advertiser account."""
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = StoreService(db)
    return await service.get_showcase_identities(ad_account)


@router.get("/showcase/{identity_id}/products")
async def get_showcase_products(
    identity_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List products within a showcase identity."""
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = StoreService(db)
    return await service.get_showcase_products(
        ad_account, identity_id, page=page, page_size=page_size
    )
