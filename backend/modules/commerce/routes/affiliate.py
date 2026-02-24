import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from backend.db.models.affiliate import AffiliateProduct
from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    AddToMarketplaceRequest,
    AffiliateProductResponse,
    CreateOpenCollaborationRequest,
    CreateTargetCollaborationRequest,
    OpenCollaborationResponse,
    PaginatedResponse,
    RespondToApplicationRequest,
    TargetCollaborationResponse,
)
from backend.modules.commerce.services.affiliate_service import AffiliateService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get(
    "/affiliate/products",
    response_model=PaginatedResponse[AffiliateProductResponse],
)
async def list_affiliate_products(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[AffiliateProductResponse]:
    service = AffiliateService(db)
    result = await service.list_affiliate_products(
        workspace_id, shop_id=shop_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[AffiliateProductResponse.model_validate(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/affiliate/marketplace/add", response_model=AffiliateProductResponse)
async def add_to_marketplace(
    workspace_id: uuid.UUID,
    body: AddToMarketplaceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AffiliateProductResponse:
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(uuid.UUID(body.shop_id))
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = AffiliateService(db)
    product = await service.add_to_marketplace(
        workspace_id,
        shop,
        product_id=body.product_id,
        commission_rate=body.commission_rate,
    )
    return AffiliateProductResponse.model_validate(product)


@router.post("/affiliate/marketplace/remove")
async def remove_from_marketplace(
    product_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    result = await db.execute(
        select(AffiliateProduct).where(AffiliateProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Affiliate product not found"
        )

    shop_service = ShopService(db)
    shop = await shop_service.get_shop(product.shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = AffiliateService(db)
    await service.remove_from_marketplace(product, shop)
    return {"removed": True}


@router.get(
    "/affiliate/collaborations",
    response_model=PaginatedResponse[OpenCollaborationResponse],
)
async def list_collaborations(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[OpenCollaborationResponse]:
    service = AffiliateService(db)
    result = await service.list_open_collaborations(
        workspace_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[OpenCollaborationResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/affiliate/collaborations/open", response_model=OpenCollaborationResponse)
async def create_open_collaboration(
    workspace_id: uuid.UUID,
    body: CreateOpenCollaborationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> OpenCollaborationResponse:
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(uuid.UUID(body.shop_id))
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = AffiliateService(db)
    collab = await service.create_open_collaboration(
        workspace_id,
        shop,
        product_id=body.product_id,
        commission_rate=body.commission_rate,
    )
    return OpenCollaborationResponse.model_validate(collab)


@router.post(
    "/affiliate/collaborations/target", response_model=TargetCollaborationResponse
)
async def create_target_collaboration(
    workspace_id: uuid.UUID,
    body: CreateTargetCollaborationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> TargetCollaborationResponse:
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(uuid.UUID(body.shop_id))
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = AffiliateService(db)
    collab = await service.create_target_collaboration(
        workspace_id,
        shop,
        product_id=body.product_id,
        creator_id=body.creator_id,
        commission_rate=body.commission_rate,
    )
    return TargetCollaborationResponse.model_validate(collab)


@router.post("/affiliate/applications/{application_id}/respond")
async def respond_to_application(
    application_id: uuid.UUID,
    body: RespondToApplicationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = AffiliateService(db)
    application = await service.respond_to_application(
        application_id, approved=body.approved
    )
    return {"status": application.status}
