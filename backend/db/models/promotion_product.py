import uuid

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class PromotionProduct(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "promotion_products"

    promotion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sku_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_skus.id", ondelete="SET NULL"),
        nullable=True,
    )
    original_price: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_price: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Per-product stock limit for this promotion",
    )

    __table_args__ = (
        Index(
            "ix_promo_products_promo_product",
            "promotion_id",
            "product_id",
            unique=True,
        ),
    )
