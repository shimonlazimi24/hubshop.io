import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    LIVE = "live"
    SELLER_DEACTIVATED = "seller_deactivated"
    PLATFORM_DEACTIVATED = "platform_deactivated"
    FROZEN = "frozen"
    DELETED = "deleted"


class OrderStatus(str, enum.Enum):
    UNPAID = "unpaid"
    ON_HOLD = "on_hold"
    AWAITING_SHIPMENT = "awaiting_shipment"
    AWAITING_COLLECTION = "awaiting_collection"
    PARTIALLY_SHIPPING = "partially_shipping"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PackageStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"


class ReturnType(str, enum.Enum):
    RETURN_AND_REFUND = "return_and_refund"
    REFUND_ONLY = "refund_only"


class ReturnStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BUYER_SHIPPED = "buyer_shipped"
    SELLER_RECEIVED = "seller_received"
    REFUNDED = "refunded"
    CLOSED = "closed"


# --- Models ---


class Shop(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "shops"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    shop_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="TikTok platform shop ID",
    )
    shop_cipher: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Encrypted shop identifier for API calls",
    )
    shop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Market region code (US, GB, etc.)",
    )
    last_product_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_order_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="shop", lazy="noload"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="shop", lazy="noload")


class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_product_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="product_status_enum"),
        nullable=False,
        default=ProductStatus.DRAFT,
    )
    main_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_amount: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Price as string to avoid float precision issues",
    )
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    inventory_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sku_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Full API snapshot for debugging",
    )

    shop: Mapped["Shop"] = relationship(back_populates="products")
    skus: Mapped[list["ProductSku"]] = relationship(
        back_populates="product", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_products_workspace_status", "workspace_id", "status"),
        Index("ix_products_workspace_created", "workspace_id", "created_at"),
    )


class ProductSku(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "product_skus"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_sku_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    seller_sku: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    inventory_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sku_name: Mapped[str | None] = mapped_column(String(500), nullable=True)

    product: Mapped["Product"] = relationship(back_populates="skus")


class Order(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "orders"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_order_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum"),
        nullable=False,
        default=OrderStatus.UNPAID,
    )
    total_amount: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Total amount as string",
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fulfillment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rts_sla: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Ready-to-ship SLA deadline",
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Full API snapshot for debugging",
    )

    shop: Mapped["Shop"] = relationship(back_populates="orders")
    line_items: Mapped[list["OrderLineItem"]] = relationship(
        back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )
    packages: Mapped[list["Package"]] = relationship(
        back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )
    status_events: Mapped[list["OrderStatusEvent"]] = relationship(
        back_populates="order", lazy="noload", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_orders_workspace_status", "workspace_id", "status"),
        Index("ix_orders_workspace_created", "workspace_id", "created_at"),
    )


class OrderLineItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "order_line_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_sku_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[str] = mapped_column(String(20), nullable=False)
    total_price: Mapped[str] = mapped_column(String(20), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="line_items")


class Package(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "packages"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_package_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    status: Mapped[PackageStatus] = mapped_column(
        Enum(PackageStatus, name="package_status_enum"),
        nullable=False,
        default=PackageStatus.PENDING,
    )
    tracking_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipping_provider: Mapped[str | None] = mapped_column(String(255), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="packages")


class OrderStatusEvent(Base, UUIDMixin):
    __tablename__ = "order_status_events"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="webhook, sync, or api",
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(back_populates="status_events")


class ReturnRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "return_requests"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_return_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    return_type: Mapped[ReturnType] = mapped_column(
        Enum(ReturnType, name="return_type_enum"),
        nullable=False,
    )
    status: Mapped[ReturnStatus] = mapped_column(
        Enum(ReturnStatus, name="return_status_enum"),
        nullable=False,
        default=ReturnStatus.PENDING,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    refund_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)

    order: Mapped["Order"] = relationship(lazy="noload")


class Promotion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "promotions"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_activity_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    promotion_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="DISCOUNT, FLASH_SALE, FREE_SHIPPING, etc."
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    discount_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="PERCENTAGE, FIXED_AMOUNT"
    )
    discount_value: Mapped[str | None] = mapped_column(String(20), nullable=True)
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_promotions_workspace_status", "workspace_id", "status"),
    )


class SyncCursor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sync_cursors"

    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    )
    sync_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="products or orders",
    )
    cursor_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_sync_cursors_shop_type", "shop_id", "sync_type", unique=True),
    )
