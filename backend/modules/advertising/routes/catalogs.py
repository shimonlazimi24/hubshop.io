import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AddProductsToCatalogRequest,
    CatalogResponse,
    CreateCatalogRequest,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.catalog_service import CatalogService
from backend.modules.commerce.schemas import PaginatedResponse

router = APIRouter()


@router.get(
    "/catalogs",
    response_model=PaginatedResponse[CatalogResponse],
)
async def list_catalogs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CatalogResponse]:
    service = CatalogService(db)
    result = await service.list_catalogs(
        workspace_id, ad_account_id=ad_account_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[CatalogResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/catalogs", response_model=CatalogResponse)
async def create_catalog(
    workspace_id: uuid.UUID,
    body: CreateCatalogRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CatalogResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = CatalogService(db)
    catalog = await service.create_catalog(workspace_id, ad_account, name=body.name)
    return CatalogResponse.model_validate(catalog)


@router.post("/catalogs/{catalog_id}/products")
async def add_products_to_catalog(
    catalog_id: uuid.UUID,
    body: AddProductsToCatalogRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CatalogService(db)
    catalog = await service.get_catalog(catalog_id)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found"
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(catalog.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    result = await service.add_products_to_catalog(
        catalog, ad_account, product_ids=body.product_ids
    )
    return result


@router.post("/catalogs/sync")
async def sync_catalogs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
) -> dict:
    account_service = AdAccountService(db)
    if ad_account_id:
        ad_account = await account_service.get_ad_account(ad_account_id)
        if not ad_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
            )
        accounts = [ad_account]
    else:
        accounts = await account_service.list_ad_accounts(workspace_id)

    service = CatalogService(db)
    total_synced = 0
    for account in accounts:
        count = await service.sync_catalogs(account)
        total_synced += count

    return {"synced": total_synced}
