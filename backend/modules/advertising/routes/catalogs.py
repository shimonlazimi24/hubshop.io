import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AddProductsToCatalogRequest,
    CatalogResponse,
    CreateCatalogRequest,
    CreateFeedRequest,
    CreateProductSetConditionRequest,
    CreateProductSetFileRequest,
    DeleteProductSetsRequest,
    UpdateFeedRequest,
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


# ---- Product Set routes ----


@router.get("/catalogs/{catalog_id}/product-sets")
async def list_product_sets(
    catalog_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
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

    return await service.list_product_sets(
        ad_account, catalog.platform_catalog_id, page=page, page_size=page_size
    )


@router.get("/catalogs/{catalog_id}/product-sets/{product_set_id}/products")
async def get_product_set_products(
    catalog_id: uuid.UUID,
    product_set_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
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

    return await service.get_product_set_products(
        ad_account,
        catalog.platform_catalog_id,
        product_set_id,
        page=page,
        page_size=page_size,
    )


@router.post("/catalogs/{catalog_id}/product-sets/by-condition")
async def create_product_set_by_condition(
    catalog_id: uuid.UUID,
    body: CreateProductSetConditionRequest,
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

    return await service.create_product_set_by_conditions(
        ad_account,
        catalog.platform_catalog_id,
        name=body.product_set_name,
        conditions=body.conditions,
    )


@router.post("/catalogs/{catalog_id}/product-sets/by-file")
async def create_product_set_by_file(
    catalog_id: uuid.UUID,
    body: CreateProductSetFileRequest,
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

    return await service.create_product_set_by_file(
        ad_account,
        catalog.platform_catalog_id,
        name=body.product_set_name,
        file_url=body.file_url,
    )


@router.delete("/catalogs/{catalog_id}/product-sets")
async def delete_product_sets(
    catalog_id: uuid.UUID,
    body: DeleteProductSetsRequest,
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

    return await service.delete_product_sets(
        ad_account,
        catalog.platform_catalog_id,
        product_set_ids=body.product_set_ids,
    )


# ---- Feed routes ----


@router.get("/catalogs/{catalog_id}/feeds")
async def list_feeds(
    catalog_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
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

    return await service.list_feeds(
        ad_account, catalog.platform_catalog_id, page=page, page_size=page_size
    )


@router.post("/catalogs/{catalog_id}/feeds")
async def create_feed(
    catalog_id: uuid.UUID,
    body: CreateFeedRequest,
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

    return await service.create_feed(
        ad_account,
        catalog.platform_catalog_id,
        feed_name=body.feed_name,
        feed_url=body.feed_url,
        auto_update=body.auto_update,
        schedule=body.schedule,
    )


@router.put("/catalogs/{catalog_id}/feeds/{feed_id}")
async def update_feed(
    catalog_id: uuid.UUID,
    feed_id: str,
    body: UpdateFeedRequest,
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

    return await service.update_feed(
        ad_account,
        catalog.platform_catalog_id,
        feed_id,
        feed_name=body.feed_name,
        feed_url=body.feed_url,
    )


@router.delete("/catalogs/{catalog_id}/feeds/{feed_id}")
async def delete_feed(
    catalog_id: uuid.UUID,
    feed_id: str,
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

    return await service.delete_feed(
        ad_account,
        catalog.platform_catalog_id,
        feed_id,
    )


@router.get("/catalogs/{catalog_id}/feeds/{feed_id}/log")
async def get_feed_log(
    catalog_id: uuid.UUID,
    feed_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
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

    return await service.get_feed_log(
        ad_account,
        catalog.platform_catalog_id,
        feed_id,
        page=page,
        page_size=page_size,
    )


# ---- Insights, Diagnostics & Event Source routes ----


class EventSourceBindRequest(BaseModel):
    event_source_id: str


@router.get("/catalogs/{catalog_id}/overview")
async def get_catalog_overview(
    catalog_id: uuid.UUID,
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

    return await service.get_catalog_overview(ad_account, catalog.platform_catalog_id)


@router.get("/catalogs/{catalog_id}/insights/trending-products")
async def get_trending_products(
    catalog_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
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

    return await service.get_trending_products(
        ad_account, catalog.platform_catalog_id, page=page, page_size=page_size
    )


@router.get("/catalogs/{catalog_id}/diagnostics")
async def get_product_diagnostics(
    catalog_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
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

    return await service.get_product_diagnostics(
        ad_account, catalog.platform_catalog_id, page=page, page_size=page_size
    )


@router.post("/catalogs/{catalog_id}/event-sources/bind")
async def bind_event_source(
    catalog_id: uuid.UUID,
    body: EventSourceBindRequest,
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

    return await service.bind_event_source(
        ad_account, catalog.platform_catalog_id, body.event_source_id
    )


@router.post("/catalogs/{catalog_id}/event-sources/unbind")
async def unbind_event_source(
    catalog_id: uuid.UUID,
    body: EventSourceBindRequest,
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

    return await service.unbind_event_source(
        ad_account, catalog.platform_catalog_id, body.event_source_id
    )
