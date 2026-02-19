from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


# --- Paginated Response ---


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Shop ---


class ShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    shop_id: str
    shop_name: str
    region: str
    last_product_sync_at: datetime | None = None
    last_order_sync_at: datetime | None = None
    created_at: datetime


# --- Product ---


class ProductSkuResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_sku_id: str
    seller_sku: str | None = None
    price_amount: str | None = None
    inventory_quantity: int
    sku_name: str | None = None


class ProductSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_product_id: str
    title: str
    status: str
    main_image_url: str | None = None
    price_amount: str | None = None
    currency: str | None = None
    inventory_total: int
    sku_count: int
    created_at: datetime
    updated_at: datetime


class ProductDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_product_id: str
    title: str
    status: str
    main_image_url: str | None = None
    price_amount: str | None = None
    currency: str | None = None
    inventory_total: int
    sku_count: int
    skus: list[ProductSkuResponse] = []
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


# --- Order ---


class OrderLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_sku_id: str | None = None
    product_name: str
    quantity: int
    unit_price: str
    total_price: str


class PackageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_package_id: str
    status: str
    tracking_number: str | None = None
    shipping_provider: str | None = None
    created_at: datetime
    updated_at: datetime


class OrderSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_order_id: str
    status: str
    total_amount: str
    currency: str
    item_count: int
    fulfillment_type: str | None = None
    rts_sla: datetime | None = None
    created_at: datetime
    updated_at: datetime


class OrderDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_order_id: str
    status: str
    total_amount: str
    currency: str
    item_count: int
    fulfillment_type: str | None = None
    rts_sla: datetime | None = None
    line_items: list[OrderLineItemResponse] = []
    packages: list[PackageResponse] = []
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class OrderTimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    from_status: str | None = None
    to_status: str
    source: str
    occurred_at: datetime


# --- Return ---


class ReturnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_return_id: str
    order_id: str
    return_type: str
    status: str
    reason: str | None = None
    refund_amount: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Analytics ---


class RevenueSummaryResponse(BaseModel):
    total_revenue: str
    total_orders: int
    average_order_value: str
    return_rate: float
    period_start: datetime
    period_end: datetime


class RevenueTimeseriesPoint(BaseModel):
    date: str
    revenue: str
    order_count: int


class TopProductResponse(BaseModel):
    product_id: str
    title: str
    total_revenue: str
    total_quantity: int
    main_image_url: str | None = None


class OrderStatusDistributionResponse(BaseModel):
    status: str
    count: int
    percentage: float


# --- Fulfillment Request ---


class ShipPackageRequest(BaseModel):
    order_id: str
    shipping_provider: str
    tracking_number: str


class MarkShippedRequest(BaseModel):
    package_id: str
    tracking_number: str | None = None


class ShippingServicesRequest(BaseModel):
    order_id: str


class ShippingServiceResponse(BaseModel):
    id: str
    name: str


# --- Return Action ---


class ReturnActionRequest(BaseModel):
    reason: str | None = None
