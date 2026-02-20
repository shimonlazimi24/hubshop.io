import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import CreatePixelRequest, PixelResponse
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.pixel_service import PixelService
from backend.modules.commerce.schemas import PaginatedResponse

router = APIRouter()


@router.get(
    "/pixels",
    response_model=PaginatedResponse[PixelResponse],
)
async def list_pixels(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[PixelResponse]:
    service = PixelService(db)
    result = await service.list_pixels(
        workspace_id, ad_account_id=ad_account_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[PixelResponse.model_validate(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/pixels", response_model=PixelResponse)
async def create_pixel(
    workspace_id: uuid.UUID,
    body: CreatePixelRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PixelResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = PixelService(db)
    pixel = await service.create_pixel(workspace_id, ad_account, name=body.name)
    return PixelResponse.model_validate(pixel)


@router.get("/pixels/{pixel_id}/code")
async def get_pixel_code(
    pixel_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = PixelService(db)
    pixel = await service.get_pixel(pixel_id)
    if not pixel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pixel not found"
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(pixel.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    code = await service.get_pixel_code(pixel, ad_account)
    return {"pixel_id": str(pixel.id), "pixel_code": code}
