from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

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
    source_platform: str = "shop"
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
    source_platform: str = "shop"
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
    source_platform: str = "shop"
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


class SplitOrderRequest(BaseModel):
    shop_id: str
    order_id: str
    groups: list[list[str]]


class BatchShipRequest(BaseModel):
    shop_id: str
    packages: list[dict]


class UpdateShippingInfoRequest(BaseModel):
    shop_id: str
    order_id: str
    tracking_number: str
    shipping_provider_id: str


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


# --- Order Cancellation ---


class CancelOrderRequest(BaseModel):
    shop_id: str
    order_id: str
    cancel_reason: str


class CancellationActionRequest(BaseModel):
    shop_id: str
    reject_reason: str | None = None


# --- Return Action ---


class ReturnActionRequest(BaseModel):
    reason: str | None = None


class CreateReturnRequest(BaseModel):
    shop_id: str
    order_id: str
    return_type: str
    reason: str


class CalculateRefundRequest(BaseModel):
    shop_id: str
    order_id: str
    items: list[dict]


# --- Affiliate ---


class AffiliateProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    commission_rate: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class AddToMarketplaceRequest(BaseModel):
    shop_id: str
    product_id: str
    commission_rate: str


class OpenCollaborationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    commission_rate: str
    status: str
    created_at: datetime
    updated_at: datetime


class CreateOpenCollaborationRequest(BaseModel):
    shop_id: str
    product_id: str
    commission_rate: str


class TargetCollaborationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    creator_id: str
    commission_rate: str
    status: str
    invite_status: str
    created_at: datetime
    updated_at: datetime


class CreateTargetCollaborationRequest(BaseModel):
    shop_id: str
    product_id: str
    creator_id: str
    commission_rate: str


class RespondToApplicationRequest(BaseModel):
    approved: bool


# --- Sample Requests (E2) ---


class SampleRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shop_id: str
    platform_request_id: str
    collaboration_id: str | None = None
    creator_id: str
    product_id: str
    status: str
    rejection_reason: str | None = None
    shipping_tracking: str | None = None
    reviewed_at: datetime | None = None
    shipped_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ReviewSampleRequest(BaseModel):
    shop_id: str
    approved: bool
    reason: str | None = None


# --- Affiliate Orders (E3) ---


class AffiliateOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shop_id: str
    platform_order_id: str
    creator_id: str
    collab_type: str
    product_id: str
    order_amount: str
    commission_rate: str
    commission_amount: str
    ordered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# --- Creator Messaging (E4) ---


class SendCreatorMessageRequest(BaseModel):
    shop_id: str
    content: str


# --- Promotions ---


class PromotionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_activity_id: str
    promotion_type: str
    title: str
    status: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    discount_type: str | None = None
    discount_value: str | None = None
    created_at: datetime
    updated_at: datetime


class CreatePromotionRequest(BaseModel):
    shop_id: str
    title: str
    promotion_type: str
    start_time: str | None = None
    end_time: str | None = None
    discount_type: str | None = None
    discount_value: str | None = None
    product_ids: list[str] | None = None


class UpdatePromotionRequest(BaseModel):
    title: str | None = None
    discount_value: str | None = None


# --- Finance ---


class SettlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_settlement_id: str
    amount: str
    currency: str
    status: str
    period_start: datetime | None = None
    period_end: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_transaction_id: str
    transaction_type: str
    amount: str
    currency: str
    order_id: str | None = None
    created_at: datetime
    updated_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_payment_id: str
    amount: str
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime


# --- Customer Service ---


class SendMessageRequest(BaseModel):
    content: str


class UpdateAgentSettingsRequest(BaseModel):
    online_hours: dict | None = None
    auto_reply_enabled: bool | None = None
    auto_reply_message: str | None = None
    greeting_message: str | None = None


# --- Product Create / Edit ---


class CreateProductRequest(BaseModel):
    shop_id: str
    title: str
    description: str
    category_id: str
    images: list[dict] = []
    skus: list[dict] = []
    package_dimensions: dict | None = None


class EditProductRequest(BaseModel):
    shop_id: str
    title: str
    description: str
    category_id: str
    images: list[dict] = []
    skus: list[dict] = []


class PartialEditProductRequest(BaseModel):
    shop_id: str
    title: str | None = None
    description: str | None = None
    images: list[dict] | None = None
    skus: list[dict] | None = None


# --- Product Lifecycle ---


class ProductBatchActionRequest(BaseModel):
    shop_id: str
    product_ids: list[str]


# --- Price & Inventory Update ---


class UpdatePriceRequest(BaseModel):
    shop_id: str
    product_id: str
    skus: list[dict]


class UpdateInventoryRequest(BaseModel):
    shop_id: str
    product_id: str
    skus: list[dict]


# --- Image & File Upload ---


class UploadImageRequest(BaseModel):
    shop_id: str
    image_url: str


class UploadFileRequest(BaseModel):
    shop_id: str
    file_url: str
    file_name: str


# --- Flash Deal schemas ---


class CreateFlashDealRequest(BaseModel):
    shop_id: str
    title: str
    product_ids: list[str]
    countdown_duration_hours: int = Field(ge=1, le=72)
    max_quantity: int | None = None
    price_rules: list[dict]
    start_time: str | None = None
    end_time: str | None = None


class CreateProductDiscountRequest(BaseModel):
    shop_id: str
    title: str
    product_ids: list[str]
    discount_type: str  # PERCENTAGE or FIXED_AMOUNT
    discount_value: str
    start_time: str | None = None
    end_time: str | None = None


class UpdatePromotionProductsRequest(BaseModel):
    product_ids: list[str]
    action: str  # ADD or REMOVE


# --- Coupon schemas ---


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_coupon_id: str
    code: str
    discount_type: str
    discount_value: str
    min_order_amount: str | None = None
    validity_start: datetime | None = None
    validity_end: datetime | None = None
    total_claim_limit: int | None = None
    per_user_limit: int | None = None
    claimed_count: int
    used_count: int
    status: str
    created_at: datetime
    updated_at: datetime
