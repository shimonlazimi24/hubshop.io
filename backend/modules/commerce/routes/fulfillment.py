import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    BatchShipRequest,
    MarkShippedRequest,
    PackageResponse,
    ShipPackageRequest,
    ShippingServiceResponse,
    ShippingServicesRequest,
    SplitOrderRequest,
    UpdateShippingInfoRequest,
)
from backend.modules.commerce.services.fulfillment_service import FulfillmentService
from backend.modules.commerce.services.order_service import OrderService

router = APIRouter()


@router.post(
    "/fulfillment/shipping-services",
    response_model=list[ShippingServiceResponse],
)
async def get_shipping_services(
    body: ShippingServicesRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ShippingServiceResponse]:
    order_service = OrderService(db)
    order = await order_service.get_order(uuid.UUID(body.order_id))
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    fulfillment = FulfillmentService(db)
    services = await fulfillment.get_eligible_shipping_services(order)
    return [ShippingServiceResponse(**s) for s in services]


@router.post("/fulfillment/ship", response_model=PackageResponse)
async def ship_package(
    body: ShipPackageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PackageResponse:
    order_service = OrderService(db)
    order = await order_service.get_order(uuid.UUID(body.order_id))
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    fulfillment = FulfillmentService(db)
    package = await fulfillment.ship_package(
        order,
        shipping_provider=body.shipping_provider,
        tracking_number=body.tracking_number,
    )
    return PackageResponse.model_validate(package)


@router.post("/fulfillment/mark-shipped", response_model=PackageResponse)
async def mark_shipped(
    body: MarkShippedRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PackageResponse:
    fulfillment = FulfillmentService(db)
    package = await fulfillment.mark_package_shipped(
        uuid.UUID(body.package_id),
        tracking_number=body.tracking_number,
    )
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found",
        )
    return PackageResponse.model_validate(package)


@router.get(
    "/fulfillment/packages/{package_id}",
    response_model=PackageResponse,
)
async def get_package(
    package_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> PackageResponse:
    fulfillment = FulfillmentService(db)
    package = await fulfillment.get_package_detail(package_id)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found",
        )
    return PackageResponse.model_validate(package)


@router.post("/fulfillment/split-order")
async def split_order(
    body: SplitOrderRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FulfillmentService(db)
    return await service.split_order(
        uuid.UUID(body.shop_id), body.order_id, body.groups
    )


@router.post("/fulfillment/batch-ship")
async def batch_ship(
    body: BatchShipRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FulfillmentService(db)
    return await service.batch_ship_packages(uuid.UUID(body.shop_id), body.packages)


@router.post("/fulfillment/packages/search")
async def search_packages(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FulfillmentService(db)
    return await service.search_packages(shop_id)


@router.get(
    "/fulfillment/packages/{package_id}/shipping-document",
)
async def get_shipping_document(
    package_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    document_type: str = "SHIPPING_LABEL",
) -> dict:
    service = FulfillmentService(db)
    return await service.get_shipping_document(shop_id, package_id, document_type)


@router.post("/fulfillment/shipping-info/update")
async def update_shipping_info(
    body: UpdateShippingInfoRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = FulfillmentService(db)
    return await service.update_shipping_info(
        uuid.UUID(body.shop_id),
        body.order_id,
        body.tracking_number,
        body.shipping_provider_id,
    )
