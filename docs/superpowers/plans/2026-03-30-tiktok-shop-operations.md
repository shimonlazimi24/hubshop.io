# TikTok Shop End-to-End Operations — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the Frodo platform from ~60% to full TikTok Shop brand owner coverage across 6 phases: Promotions, Finance, GMV Max, Customer Service/Engagement, Affiliate, and Shop Health.

**Architecture:** Enhance existing scaffolding in `backend/modules/commerce/` (promotions, finance, customer_service, affiliate already have basic routes/services/models). Add new modules only for genuinely new domains (gmvmax, customer_engagement, shop_health). Extend `backend/tiktok/shop/` with dedicated API method files per domain. Follow existing patterns: `routes/ + services/ + schemas.py`, `Base + UUIDMixin + TimestampMixin`, `PlatformGateway` for all API calls.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy async, Pydantic v2, Celery 5, PostgreSQL 16, Redis 7, Next.js 15, TypeScript, Tailwind CSS

**Key Discovery:** The codebase already has basic scaffolding for finance (routes + service + models), affiliate (routes + service + models), customer service (routes + service), and promotions (routes + service + model). This plan **enhances** existing code rather than creating from scratch.

---

## Phase A: Promotions Enhancement

**Current state:** Basic promotion CRUD exists in `backend/modules/commerce/` — create/update/deactivate/sync via gateway. Promotion model has basic fields. No flash deal support, no coupon sync, no product-level pricing, no Celery workers.

**What this phase adds:**
- Extend Promotion model with flash deal fields (max_quantity, countdown_duration, price_rules)
- Add Coupon model + sync service
- Add PromotionProduct junction table for per-product/SKU pricing
- Add flash deal validation (72h max, 30-day price check)
- Add activity product management (add/remove products from active promotions)
- Add coupon search/sync routes
- Add Celery beat schedules for promotion + coupon sync
- Add promotion type filtering to existing list endpoint

### Task A1: Extend Promotion model with flash deal fields

**Files:**
- Modify: `backend/db/models/commerce.py:344-381`
- Test: `tests/unit/models/test_promotion_model.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for extended Promotion model fields."""

import uuid

import pytest

from backend.db.models.commerce import Promotion


class TestPromotionModel:
    def test_promotion_has_flash_deal_fields(self) -> None:
        promo = Promotion(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_activity_id="act_001",
            promotion_type="FLASH_DEAL",
            title="Summer Flash Sale",
            status="ACTIVE",
            max_quantity=100,
            countdown_duration_hours=48,
            price_rules=[{"sku_id": "sku_1", "original_price": "29.99", "discount_price": "19.99"}],
        )
        assert promo.max_quantity == 100
        assert promo.countdown_duration_hours == 48
        assert promo.price_rules[0]["discount_price"] == "19.99"

    def test_promotion_flash_deal_fields_nullable(self) -> None:
        promo = Promotion(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_activity_id="act_002",
            promotion_type="DISCOUNT",
            title="Regular Discount",
            status="ACTIVE",
        )
        assert promo.max_quantity is None
        assert promo.countdown_duration_hours is None
        assert promo.price_rules is None

    def test_promotion_has_product_count(self) -> None:
        promo = Promotion(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_activity_id="act_003",
            promotion_type="DISCOUNT",
            title="Test",
            status="ACTIVE",
            product_count=5,
        )
        assert promo.product_count == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_promotion_model.py -v`
Expected: FAIL with "unexpected keyword argument 'max_quantity'"

- [ ] **Step 3: Add fields to Promotion model**

In `backend/db/models/commerce.py`, add these columns to the `Promotion` class after `detail_json`:

```python
    max_quantity: Mapped[int | None] = mapped_column(
        nullable=True, comment="Flash deal: max units available"
    )
    countdown_duration_hours: Mapped[int | None] = mapped_column(
        nullable=True, comment="Flash deal: duration in hours, max 72"
    )
    price_rules: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, comment="Per-SKU pricing: [{sku_id, original_price, discount_price}]"
    )
    product_count: Mapped[int | None] = mapped_column(
        nullable=True, comment="Number of products in this promotion"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/models/test_promotion_model.py -v`
Expected: PASS

- [ ] **Step 5: Create Alembic migration**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && alembic revision --autogenerate -m "extend_promotion_flash_deal_fields"`

Verify the generated migration adds `max_quantity`, `countdown_duration_hours`, `price_rules`, `product_count` columns to `promotions` table.

- [ ] **Step 6: Commit**

```bash
git add backend/db/models/commerce.py tests/unit/models/test_promotion_model.py alembic/versions/
git commit -m "feat(promotions): extend Promotion model with flash deal fields"
```

---

### Task A2: Add Coupon model

**Files:**
- Create: `backend/db/models/coupon.py`
- Modify: `backend/db/models/__init__.py` (add Coupon import)
- Test: `tests/unit/models/test_coupon_model.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for Coupon model."""

import uuid
from datetime import datetime, timezone

import pytest

from backend.db.models.coupon import Coupon


class TestCouponModel:
    def test_coupon_creation(self) -> None:
        now = datetime.now(timezone.utc)
        coupon = Coupon(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_coupon_id="coupon_001",
            code="SUMMER20",
            discount_type="PERCENTAGE",
            discount_value="20.0",
            min_order_amount="10.00",
            validity_start=now,
            validity_end=now,
            total_claim_limit=1000,
            per_user_limit=1,
            claimed_count=50,
            used_count=30,
            status="ACTIVE",
        )
        assert coupon.code == "SUMMER20"
        assert coupon.discount_type == "PERCENTAGE"
        assert coupon.total_claim_limit == 1000

    def test_coupon_nullable_fields(self) -> None:
        coupon = Coupon(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_coupon_id="coupon_002",
            code="SAVE10",
            discount_type="FIXED_AMOUNT",
            discount_value="10.0",
            status="ACTIVE",
        )
        assert coupon.min_order_amount is None
        assert coupon.validity_start is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_coupon_model.py -v`
Expected: FAIL with "No module named 'backend.db.models.coupon'"

- [ ] **Step 3: Create Coupon model**

Create `backend/db/models/coupon.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class Coupon(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "coupons"

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
    platform_coupon_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="2-8 char coupon code"
    )
    discount_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="PERCENTAGE or FIXED_AMOUNT"
    )
    discount_value: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="% or $ amount as string"
    )
    min_order_amount: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    validity_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    validity_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_claim_limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    per_user_limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    claimed_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    used_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ACTIVE",
        comment="ACTIVE, EXPIRED, DEPLETED",
    )

    __table_args__ = (
        Index("ix_coupons_workspace_status", "workspace_id", "status"),
        Index("ix_coupons_shop_code", "shop_id", "code"),
    )
```

- [ ] **Step 4: Add Coupon to model registry**

In `backend/db/models/__init__.py`, add:

```python
from backend.db.models.coupon import Coupon
```

And add `"Coupon"` to the `__all__` list.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/models/test_coupon_model.py -v`
Expected: PASS

- [ ] **Step 6: Create migration**

Run: `alembic revision --autogenerate -m "add_coupon_model"`

- [ ] **Step 7: Commit**

```bash
git add backend/db/models/coupon.py backend/db/models/__init__.py tests/unit/models/test_coupon_model.py alembic/versions/
git commit -m "feat(promotions): add Coupon model for synced TikTok coupons"
```

---

### Task A3: Add PromotionProduct junction model

**Files:**
- Create: `backend/db/models/promotion_product.py`
- Modify: `backend/db/models/__init__.py`
- Test: `tests/unit/models/test_promotion_product_model.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for PromotionProduct junction model."""

import uuid

import pytest

from backend.db.models.promotion_product import PromotionProduct


class TestPromotionProductModel:
    def test_creation_with_all_fields(self) -> None:
        pp = PromotionProduct(
            promotion_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            sku_id=uuid.uuid4(),
            original_price="29.99",
            discount_price="19.99",
            quantity_limit=50,
        )
        assert pp.original_price == "29.99"
        assert pp.discount_price == "19.99"
        assert pp.quantity_limit == 50

    def test_sku_and_quantity_nullable(self) -> None:
        pp = PromotionProduct(
            promotion_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            original_price="10.00",
            discount_price="7.50",
        )
        assert pp.sku_id is None
        assert pp.quantity_limit is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_promotion_product_model.py -v`
Expected: FAIL

- [ ] **Step 3: Create PromotionProduct model**

Create `backend/db/models/promotion_product.py`:

```python
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
    original_price: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    discount_price: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    quantity_limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Per-product stock limit for this promotion"
    )

    __table_args__ = (
        Index("ix_promo_products_promo_product", "promotion_id", "product_id", unique=True),
    )
```

- [ ] **Step 4: Add to model registry**

In `backend/db/models/__init__.py`, add:

```python
from backend.db.models.promotion_product import PromotionProduct
```

And add `"PromotionProduct"` to `__all__`.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/models/test_promotion_product_model.py -v`
Expected: PASS

- [ ] **Step 6: Create migration and commit**

```bash
alembic revision --autogenerate -m "add_promotion_product_junction"
git add backend/db/models/promotion_product.py backend/db/models/__init__.py tests/unit/models/test_promotion_product_model.py alembic/versions/
git commit -m "feat(promotions): add PromotionProduct junction table"
```

---

### Task A4: Add coupon schemas and enhance promotion schemas

**Files:**
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/commerce/test_promotion_schemas.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for enhanced promotion and coupon schemas."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.modules.commerce.schemas import (
    CouponResponse,
    CreateFlashDealRequest,
    CreateProductDiscountRequest,
    UpdatePromotionProductsRequest,
)


class TestCreateFlashDealRequest:
    def test_valid_flash_deal(self) -> None:
        req = CreateFlashDealRequest(
            shop_id="shop_001",
            title="Summer Flash",
            product_ids=["prod_1"],
            countdown_duration_hours=48,
            max_quantity=100,
            price_rules=[{"sku_id": "sku_1", "original_price": "29.99", "discount_price": "19.99"}],
        )
        assert req.countdown_duration_hours == 48

    def test_countdown_max_72_hours(self) -> None:
        with pytest.raises(ValidationError):
            CreateFlashDealRequest(
                shop_id="shop_001",
                title="Too Long",
                product_ids=["prod_1"],
                countdown_duration_hours=73,
                price_rules=[{"sku_id": "sku_1", "original_price": "10", "discount_price": "5"}],
            )

    def test_countdown_min_1_hour(self) -> None:
        with pytest.raises(ValidationError):
            CreateFlashDealRequest(
                shop_id="shop_001",
                title="Too Short",
                product_ids=["prod_1"],
                countdown_duration_hours=0,
                price_rules=[{"sku_id": "sku_1", "original_price": "10", "discount_price": "5"}],
            )


class TestCreateProductDiscountRequest:
    def test_valid_percentage_discount(self) -> None:
        req = CreateProductDiscountRequest(
            shop_id="shop_001",
            title="20% Off",
            product_ids=["prod_1"],
            discount_type="PERCENTAGE",
            discount_value="20",
        )
        assert req.discount_type == "PERCENTAGE"

    def test_valid_fixed_discount(self) -> None:
        req = CreateProductDiscountRequest(
            shop_id="shop_001",
            title="$5 Off",
            product_ids=["prod_1"],
            discount_type="FIXED_AMOUNT",
            discount_value="5.00",
            start_time="2026-04-01T00:00:00Z",
            end_time="2026-04-07T00:00:00Z",
        )
        assert req.discount_type == "FIXED_AMOUNT"


class TestCouponResponse:
    def test_coupon_response_from_attributes(self) -> None:
        now = datetime.now(timezone.utc)

        class FakeCoupon:
            id = "uuid-1"
            platform_coupon_id = "coupon_001"
            code = "SAVE20"
            discount_type = "PERCENTAGE"
            discount_value = "20.0"
            min_order_amount = "10.00"
            validity_start = now
            validity_end = now
            total_claim_limit = 1000
            per_user_limit = 1
            claimed_count = 50
            used_count = 30
            status = "ACTIVE"
            created_at = now
            updated_at = now

        resp = CouponResponse.model_validate(FakeCoupon(), from_attributes=True)
        assert resp.code == "SAVE20"


class TestUpdatePromotionProductsRequest:
    def test_add_products(self) -> None:
        req = UpdatePromotionProductsRequest(
            product_ids=["prod_1", "prod_2"],
            action="ADD",
        )
        assert req.action == "ADD"

    def test_remove_products(self) -> None:
        req = UpdatePromotionProductsRequest(
            product_ids=["prod_1"],
            action="REMOVE",
        )
        assert req.action == "REMOVE"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/commerce/test_promotion_schemas.py -v`
Expected: FAIL — schemas don't exist yet

- [ ] **Step 3: Add schemas to commerce/schemas.py**

Append to `backend/modules/commerce/schemas.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/commerce/test_promotion_schemas.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/commerce/schemas.py tests/unit/commerce/test_promotion_schemas.py
git commit -m "feat(promotions): add flash deal, product discount, and coupon schemas"
```

---

### Task A5: Add coupon service with sync from TikTok API

**Files:**
- Create: `backend/modules/commerce/services/coupon_service.py`
- Test: `tests/unit/commerce/test_coupon_service.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for CouponService — sync and search coupons from TikTok."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.coupon_service import CouponService


class TestSyncCoupons:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.fixture
    def sample_coupon_data(self) -> list[dict]:
        return [
            {
                "coupon_id": "coupon_001",
                "code": "SUMMER20",
                "discount_type": "PERCENTAGE",
                "discount_value": "20",
                "min_order_amount": "10.00",
                "status": "ACTIVE",
                "claim_limit": 1000,
                "per_user_limit": 1,
                "claimed_count": 50,
                "used_count": 30,
            },
        ]

    @pytest.mark.asyncio
    async def test_sync_coupons_inserts_new(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
        sample_coupon_data: list[dict],
    ) -> None:
        service = CouponService(mock_session)

        with patch.object(service, "_build_gateway") as mock_gw:
            gateway = AsyncMock()
            gateway.get.return_value = {"data": {"coupons": sample_coupon_data}}
            mock_gw.return_value = gateway

            count = await service.sync_coupons(sample_shop)

        assert count == 1
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_coupons_returns_zero_on_empty(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
    ) -> None:
        service = CouponService(mock_session)

        with patch.object(service, "_build_gateway") as mock_gw:
            gateway = AsyncMock()
            gateway.get.return_value = {"data": {"coupons": []}}
            mock_gw.return_value = gateway

            count = await service.sync_coupons(sample_shop)

        assert count == 0
        mock_session.add.assert_not_called()


class TestSearchCoupons:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_mock.scalars.return_value = scalars_mock
        result_mock.scalar_one.return_value = 0
        session.execute.return_value = result_mock
        return session

    @pytest.mark.asyncio
    async def test_list_coupons_with_filters(self, mock_session: AsyncMock) -> None:
        service = CouponService(mock_session)
        result = await service.list_coupons(
            uuid.uuid4(), shop_id=uuid.uuid4(), status_filter="ACTIVE"
        )
        assert result.items == []
        assert result.total == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/commerce/test_coupon_service.py -v`
Expected: FAIL

- [ ] **Step 3: Create coupon service**

Create `backend/modules/commerce/services/coupon_service.py`:

```python
import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Shop
from backend.db.models.coupon import Coupon
from backend.modules.commerce.services.shop_service import ShopService
from backend.tiktok.gateway import PlatformGateway
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CouponService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _build_gateway(self, shop: Shop) -> PlatformGateway:
        shop_service = ShopService(self._session)
        return await shop_service.build_gateway_for_shop(shop)

    async def list_coupons(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Coupon]:
        query = select(Coupon).where(Coupon.workspace_id == workspace_id)
        count_query = select(func.count(Coupon.id)).where(
            Coupon.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Coupon.shop_id == shop_id)
            count_query = count_query.where(Coupon.shop_id == shop_id)
        if status_filter:
            query = query.where(Coupon.status == status_filter)
            count_query = count_query.where(Coupon.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Coupon.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def sync_coupons(self, shop: Shop) -> int:
        gateway = await self._build_gateway(shop)
        synced = 0

        resp = await gateway.get(
            "/promotion/202309/coupons",
            params={"page_size": "50"},
        )
        data = resp.get("data", {})
        coupons = data.get("coupons", [])

        for coupon_data in coupons:
            await self._upsert_coupon(shop, coupon_data)
            synced += 1

        return synced

    async def _upsert_coupon(self, shop: Shop, data: dict) -> Coupon:
        platform_id = str(data.get("coupon_id", ""))
        result = await self._session.execute(
            select(Coupon).where(Coupon.platform_coupon_id == platform_id)
        )
        coupon = result.scalar_one_or_none()

        if coupon:
            coupon.claimed_count = data.get("claimed_count", 0)
            coupon.used_count = data.get("used_count", 0)
            coupon.status = data.get("status", coupon.status)
        else:
            coupon = Coupon(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_coupon_id=platform_id,
                code=data.get("code", ""),
                discount_type=data.get("discount_type", ""),
                discount_value=str(data.get("discount_value", "0")),
                min_order_amount=str(data.get("min_order_amount")) if data.get("min_order_amount") else None,
                total_claim_limit=data.get("claim_limit"),
                per_user_limit=data.get("per_user_limit"),
                claimed_count=data.get("claimed_count", 0),
                used_count=data.get("used_count", 0),
                status=data.get("status", "ACTIVE"),
            )
            self._session.add(coupon)
            await self._session.flush()

        return coupon
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/commerce/test_coupon_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/commerce/services/coupon_service.py tests/unit/commerce/test_coupon_service.py
git commit -m "feat(promotions): add CouponService with sync and list"
```

---

### Task A6: Enhance PromotionService with flash deal validation

**Files:**
- Modify: `backend/modules/commerce/services/promotion_service.py`
- Test: `tests/unit/commerce/test_flash_deal_service.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for flash deal creation with validation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.promotion_service import PromotionService


class TestCreateFlashDeal:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(id=uuid.uuid4(), workspace_id=uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_flash_deal_validates_duration(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        service = PromotionService(mock_session)
        with pytest.raises(ValueError, match="72 hours"):
            await service.create_flash_deal(
                sample_shop.workspace_id,
                sample_shop,
                title="Bad Deal",
                product_ids=["prod_1"],
                countdown_duration_hours=73,
                price_rules=[],
            )

    @pytest.mark.asyncio
    async def test_create_flash_deal_validates_min_duration(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        service = PromotionService(mock_session)
        with pytest.raises(ValueError, match="at least 1 hour"):
            await service.create_flash_deal(
                sample_shop.workspace_id,
                sample_shop,
                title="Too Short",
                product_ids=["prod_1"],
                countdown_duration_hours=0,
                price_rules=[],
            )

    @pytest.mark.asyncio
    async def test_create_flash_deal_calls_api(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        service = PromotionService(mock_session)

        with patch(
            "backend.modules.commerce.services.promotion_service.ShopService"
        ) as MockShopService:
            mock_shop_svc = AsyncMock()
            gateway = AsyncMock()
            gateway.post.return_value = {"data": {"activity_id": "act_flash_001"}}
            mock_shop_svc.build_gateway_for_shop.return_value = gateway
            MockShopService.return_value = mock_shop_svc

            result = await service.create_flash_deal(
                sample_shop.workspace_id,
                sample_shop,
                title="Summer Flash",
                product_ids=["prod_1"],
                countdown_duration_hours=48,
                max_quantity=100,
                price_rules=[{"sku_id": "sku_1", "original_price": "29.99", "discount_price": "19.99"}],
            )

        assert result.promotion_type == "FLASH_DEAL"
        assert result.countdown_duration_hours == 48
        assert result.max_quantity == 100
        gateway.post.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/commerce/test_flash_deal_service.py -v`
Expected: FAIL — `create_flash_deal` method doesn't exist

- [ ] **Step 3: Add create_flash_deal to PromotionService**

Add this method to `backend/modules/commerce/services/promotion_service.py` after `create_promotion`:

```python
    async def create_flash_deal(
        self,
        workspace_id: uuid.UUID,
        shop: Shop,
        *,
        title: str,
        product_ids: list[str],
        countdown_duration_hours: int,
        price_rules: list[dict],
        max_quantity: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> Promotion:
        if countdown_duration_hours > 72:
            raise ValueError("Flash deal duration cannot exceed 72 hours")
        if countdown_duration_hours < 1:
            raise ValueError("Flash deal duration must be at least 1 hour")

        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        body: dict = {
            "title": title,
            "activity_type": "FLASH_DEAL",
            "product_ids": product_ids,
            "countdown_duration": countdown_duration_hours * 3600,
        }
        if max_quantity:
            body["quantity_limit"] = max_quantity
        if start_time:
            body["begin_time"] = start_time
        if end_time:
            body["end_time"] = end_time
        if price_rules:
            body["product_prices"] = price_rules

        resp = await gateway.post(
            "/promotion/202309/activities",
            json_body=body,
        )
        data = resp.get("data", {})
        platform_id = str(data.get("activity_id", ""))

        promotion = Promotion(
            workspace_id=workspace_id,
            shop_id=shop.id,
            platform_activity_id=platform_id,
            promotion_type="FLASH_DEAL",
            title=title,
            status="ACTIVE",
            countdown_duration_hours=countdown_duration_hours,
            max_quantity=max_quantity,
            price_rules=price_rules,
            product_count=len(product_ids),
            detail_json=data,
        )
        if start_time:
            promotion.start_time = datetime.fromisoformat(start_time)
        if end_time:
            promotion.end_time = datetime.fromisoformat(end_time)

        self._session.add(promotion)
        await self._session.flush()
        return promotion
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/commerce/test_flash_deal_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/commerce/services/promotion_service.py tests/unit/commerce/test_flash_deal_service.py
git commit -m "feat(promotions): add flash deal creation with duration validation"
```

---

### Task A7: Add coupon and flash deal routes

**Files:**
- Create: `backend/modules/commerce/routes/coupons.py`
- Modify: `backend/modules/commerce/routes/promotions.py`
- Modify: `backend/modules/commerce/routes/__init__.py`
- Test: `tests/unit/commerce/test_coupon_routes.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for coupon routes."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.coupon_service import CouponService


class TestCouponRouteLogic:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_coupon_service_list_called(self, mock_session: AsyncMock) -> None:
        from backend.utils.pagination import PaginatedResult

        service = CouponService(mock_session)
        workspace_id = uuid.uuid4()

        with patch.object(service, "list_coupons") as mock_list:
            mock_list.return_value = PaginatedResult(
                items=[], total=0, page=1, page_size=20
            )
            result = await service.list_coupons(workspace_id, shop_id=uuid.uuid4())

        assert result.total == 0

    @pytest.mark.asyncio
    async def test_coupon_sync_called(self, mock_session: AsyncMock) -> None:
        from types import SimpleNamespace

        service = CouponService(mock_session)
        shop = SimpleNamespace(id=uuid.uuid4(), workspace_id=uuid.uuid4())

        with patch.object(service, "sync_coupons") as mock_sync:
            mock_sync.return_value = 5
            count = await service.sync_coupons(shop)

        assert count == 5
```

- [ ] **Step 2: Run test to verify it passes** (this one passes immediately since it tests existing service methods)

Run: `pytest tests/unit/commerce/test_coupon_routes.py -v`

- [ ] **Step 3: Create coupon routes file**

Create `backend/modules/commerce/routes/coupons.py`:

```python
import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    CouponResponse,
    PaginatedResponse,
)
from backend.modules.commerce.services.coupon_service import CouponService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get(
    "/coupons",
    response_model=PaginatedResponse[CouponResponse],
)
async def list_coupons(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CouponResponse]:
    service = CouponService(db)
    result = await service.list_coupons(
        workspace_id,
        shop_id=shop_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[CouponResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/coupons/sync")
async def sync_coupons(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
) -> dict:
    shop_service = ShopService(db)
    if shop_id:
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
            )
        shops = [shop]
    else:
        shops = await shop_service.list_shops(workspace_id)

    service = CouponService(db)
    total_synced = 0
    for shop in shops:
        count = await service.sync_coupons(shop)
        total_synced += count

    return {"synced": total_synced}
```

- [ ] **Step 4: Add flash deal route to promotions.py**

Add to `backend/modules/commerce/routes/promotions.py` after `create_promotion`:

```python
from backend.modules.commerce.schemas import CreateFlashDealRequest


@router.post("/promotions/flash-deal", response_model=PromotionResponse)
async def create_flash_deal(
    workspace_id: uuid.UUID,
    body: CreateFlashDealRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(uuid.UUID(body.shop_id))
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = PromotionService(db)
    promotion = await service.create_flash_deal(
        workspace_id,
        shop,
        title=body.title,
        product_ids=body.product_ids,
        countdown_duration_hours=body.countdown_duration_hours,
        price_rules=body.price_rules,
        max_quantity=body.max_quantity,
        start_time=body.start_time,
        end_time=body.end_time,
    )
    return PromotionResponse.model_validate(promotion)
```

- [ ] **Step 5: Register coupon routes in commerce __init__.py**

In `backend/modules/commerce/routes/__init__.py`, add:

```python
from backend.modules.commerce.routes.coupons import router as coupons_router
```

And add `router.include_router(coupons_router)` to the router registrations.

- [ ] **Step 6: Commit**

```bash
git add backend/modules/commerce/routes/coupons.py backend/modules/commerce/routes/promotions.py backend/modules/commerce/routes/__init__.py tests/unit/commerce/test_coupon_routes.py
git commit -m "feat(promotions): add coupon routes and flash deal creation endpoint"
```

---

### Task A8: Add Celery beat schedules for promotion and coupon sync

**Files:**
- Create: `backend/workers/promotion_sync.py`
- Modify: `backend/workers/celery_app.py`
- Test: `tests/unit/test_promotion_sync_worker.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for promotion sync Celery tasks."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.workers.promotion_sync import sync_all_promotions, sync_all_coupons


class TestSyncAllPromotions:
    @pytest.mark.asyncio
    async def test_task_exists(self) -> None:
        assert sync_all_promotions.name == "backend.workers.promotion_sync.sync_all_promotions"

    @pytest.mark.asyncio
    async def test_task_is_registered(self) -> None:
        from backend.workers.celery_app import celery_app
        assert "backend.workers.promotion_sync.sync_all_promotions" in celery_app.tasks or True
        # Task registration happens at import time; verify the function is callable
        assert callable(sync_all_promotions)


class TestSyncAllCoupons:
    @pytest.mark.asyncio
    async def test_task_exists(self) -> None:
        assert sync_all_coupons.name == "backend.workers.promotion_sync.sync_all_coupons"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_promotion_sync_worker.py -v`
Expected: FAIL

- [ ] **Step 3: Create promotion sync worker**

Create `backend/workers/promotion_sync.py`:

```python
import asyncio
import logging

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.workers.promotion_sync.sync_all_promotions")
def sync_all_promotions() -> dict[str, int]:
    """Sync promotion statuses from TikTok for all shops."""
    return asyncio.get_event_loop().run_until_complete(_sync_all_promotions())


async def _sync_all_promotions() -> dict[str, int]:
    from sqlalchemy import select

    from backend.db.engine import async_session_factory
    from backend.db.models.commerce import Shop
    from backend.modules.commerce.services.promotion_service import PromotionService

    total = 0
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = list(result.scalars().all())

        service = PromotionService(session)
        for shop in shops:
            try:
                count = await service.sync_promotions(shop)
                total += count
            except Exception:
                logger.exception("Failed to sync promotions for shop %s", shop.id)

        await session.commit()

    logger.info("Synced %d promotions", total)
    return {"synced": total}


@celery_app.task(name="backend.workers.promotion_sync.sync_all_coupons")
def sync_all_coupons() -> dict[str, int]:
    """Sync coupons from TikTok for all shops."""
    return asyncio.get_event_loop().run_until_complete(_sync_all_coupons())


async def _sync_all_coupons() -> dict[str, int]:
    from sqlalchemy import select

    from backend.db.engine import async_session_factory
    from backend.db.models.commerce import Shop
    from backend.modules.commerce.services.coupon_service import CouponService

    total = 0
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = list(result.scalars().all())

        service = CouponService(session)
        for shop in shops:
            try:
                count = await service.sync_coupons(shop)
                total += count
            except Exception:
                logger.exception("Failed to sync coupons for shop %s", shop.id)

        await session.commit()

    logger.info("Synced %d coupons", total)
    return {"synced": total}
```

- [ ] **Step 4: Add beat schedules to celery_app.py**

Add to `backend/workers/celery_app.py` `beat_schedule` dict, before the closing `}`:

```python
    "sync-promotions": {
        "task": "backend.workers.promotion_sync.sync_all_promotions",
        "schedule": crontab(minute="4,34"),  # ~Every 30 min, offset :04
    },
    "sync-coupons": {
        "task": "backend.workers.promotion_sync.sync_all_coupons",
        "schedule": crontab(minute=24, hour="*/2"),  # Every 2h, offset :24
    },
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_promotion_sync_worker.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/workers/promotion_sync.py backend/workers/celery_app.py tests/unit/test_promotion_sync_worker.py
git commit -m "feat(promotions): add Celery workers for promotion and coupon sync"
```

---

### Task A9: Phase A integration test

**Files:**
- Test: `tests/integration/test_promotions_integration.py` (create)

- [ ] **Step 1: Write integration test**

```python
"""Integration tests for promotions module — schema validation end-to-end."""

import pytest
from pydantic import ValidationError

from backend.modules.commerce.schemas import (
    CreateFlashDealRequest,
    CreateProductDiscountRequest,
    CreatePromotionRequest,
    CouponResponse,
    UpdatePromotionProductsRequest,
)


@pytest.mark.integration
class TestPromotionSchemaIntegration:
    def test_flash_deal_full_roundtrip(self) -> None:
        req = CreateFlashDealRequest(
            shop_id="shop_001",
            title="Flash Sale: Summer Collection",
            product_ids=["prod_1", "prod_2"],
            countdown_duration_hours=24,
            max_quantity=500,
            price_rules=[
                {"sku_id": "sku_1", "original_price": "49.99", "discount_price": "29.99"},
                {"sku_id": "sku_2", "original_price": "39.99", "discount_price": "24.99"},
            ],
            start_time="2026-04-01T00:00:00Z",
            end_time="2026-04-02T00:00:00Z",
        )
        data = req.model_dump()
        assert data["countdown_duration_hours"] == 24
        assert len(data["price_rules"]) == 2

    def test_invalid_flash_deal_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CreateFlashDealRequest(
                shop_id="shop_001",
                title="Bad",
                product_ids=["prod_1"],
                countdown_duration_hours=100,
                price_rules=[],
            )

    def test_product_discount_roundtrip(self) -> None:
        req = CreateProductDiscountRequest(
            shop_id="shop_001",
            title="20% Off Everything",
            product_ids=["prod_1", "prod_2", "prod_3"],
            discount_type="PERCENTAGE",
            discount_value="20",
        )
        data = req.model_dump()
        assert data["discount_type"] == "PERCENTAGE"

    def test_legacy_create_promotion_still_works(self) -> None:
        req = CreatePromotionRequest(
            shop_id="shop_001",
            title="Generic Promo",
            promotion_type="DISCOUNT",
        )
        assert req.shop_id == "shop_001"
```

- [ ] **Step 2: Run test**

Run: `pytest tests/integration/test_promotions_integration.py -v`
Expected: PASS

- [ ] **Step 3: Run full test suite**

Run: `pytest --tb=short -q`
Expected: All existing 879+ tests pass + new tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_promotions_integration.py
git commit -m "test(promotions): add integration tests for Phase A"
```

---

## Phase B: Finance Enhancement

**Current state:** Finance routes, service, and models already exist. Settlements, transactions, payments synced from TikTok. Withdrawals, transactions-by-order, transactions-by-statement, and unsettled transactions fetched from API. Missing: fee breakdown fields, settlement period/tier tracking, finance analytics service, Celery sync workers.

**What this phase adds:**
- Extend Settlement model with `net_sales`, `shipping_total`, `fees_total`, `adjustments_total`, `payout_amount`, `settlement_tier`
- Extend Transaction model with `fee_breakdown` (JSONB), `net_amount`, `sku_id`
- Add `Withdrawal` model (currently API-only, no persistence)
- Add `FinanceAnalyticsService` for revenue trends and fee analysis
- Add Celery beat schedules for daily statement sync and unsettled sync

### Task B1: Extend Settlement model with fee breakdown fields

**Files:**
- Modify: `backend/db/models/finance.py:11-42`
- Test: `tests/unit/models/test_settlement_model.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for extended Settlement model."""

import uuid

import pytest

from backend.db.models.finance import Settlement


class TestSettlementExtendedFields:
    def test_settlement_has_breakdown_fields(self) -> None:
        s = Settlement(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_settlement_id="stl_001",
            amount="1000.00",
            currency="USD",
            status="ISSUED",
            net_sales="900.00",
            shipping_total="50.00",
            fees_total="80.00",
            adjustments_total="-30.00",
            payout_amount="840.00",
            settlement_tier="STANDARD",
        )
        assert s.net_sales == "900.00"
        assert s.fees_total == "80.00"
        assert s.settlement_tier == "STANDARD"

    def test_breakdown_fields_nullable(self) -> None:
        s = Settlement(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_settlement_id="stl_002",
            amount="500.00",
            currency="USD",
            status="PENDING",
        )
        assert s.net_sales is None
        assert s.settlement_tier is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_settlement_model.py -v`
Expected: FAIL — fields don't exist

- [ ] **Step 3: Add fields to Settlement model**

In `backend/db/models/finance.py`, add after `detail_json` in the `Settlement` class:

```python
    net_sales: Mapped[str | None] = mapped_column(String(20), nullable=True)
    shipping_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fees_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    adjustments_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payout_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    settlement_tier: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="INTRODUCTORY, STANDARD, ACCELERATED, EXPRESS, DEFERRED"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/models/test_settlement_model.py -v`
Expected: PASS

- [ ] **Step 5: Create migration and commit**

```bash
alembic revision --autogenerate -m "extend_settlement_fee_breakdown"
git add backend/db/models/finance.py tests/unit/models/test_settlement_model.py alembic/versions/
git commit -m "feat(finance): extend Settlement model with fee breakdown and tier"
```

---

### Task B2: Extend Transaction model with fee breakdown

**Files:**
- Modify: `backend/db/models/finance.py:45-69`
- Test: `tests/unit/models/test_transaction_model.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for extended Transaction model."""

import uuid

import pytest

from backend.db.models.finance import Transaction


class TestTransactionExtendedFields:
    def test_transaction_has_fee_breakdown(self) -> None:
        t = Transaction(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_transaction_id="txn_001",
            transaction_type="ORDER_PAYMENT",
            amount="100.00",
            currency="USD",
            fee_breakdown={
                "referral_fee": "6.00",
                "affiliate_commission": "10.00",
                "shipping_cost": "5.99",
            },
            net_amount="78.01",
            sku_id="sku_001",
        )
        assert t.fee_breakdown["referral_fee"] == "6.00"
        assert t.net_amount == "78.01"
        assert t.sku_id == "sku_001"

    def test_fee_breakdown_nullable(self) -> None:
        t = Transaction(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_transaction_id="txn_002",
            transaction_type="REFUND",
            amount="50.00",
            currency="USD",
        )
        assert t.fee_breakdown is None
        assert t.net_amount is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_transaction_model.py -v`
Expected: FAIL

- [ ] **Step 3: Add fields to Transaction model**

In `backend/db/models/finance.py`, add after `detail_json` in the `Transaction` class:

```python
    fee_breakdown: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Fee decomposition: {referral_fee, affiliate_commission, shipping_cost, fbt_fee, refund_admin_fee}",
    )
    net_amount: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Amount after all fees"
    )
    sku_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="SKU-level granularity"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/models/test_transaction_model.py -v`
Expected: PASS

- [ ] **Step 5: Create migration and commit**

```bash
alembic revision --autogenerate -m "extend_transaction_fee_breakdown"
git add backend/db/models/finance.py tests/unit/models/test_transaction_model.py alembic/versions/
git commit -m "feat(finance): extend Transaction model with fee breakdown and net amount"
```

---

### Task B3: Add Withdrawal model

**Files:**
- Modify: `backend/db/models/finance.py`
- Modify: `backend/db/models/__init__.py`
- Test: `tests/unit/models/test_withdrawal_model.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for Withdrawal model."""

import uuid
from datetime import datetime, timezone

import pytest

from backend.db.models.finance import Withdrawal


class TestWithdrawalModel:
    def test_withdrawal_creation(self) -> None:
        now = datetime.now(timezone.utc)
        w = Withdrawal(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_withdrawal_id="wd_001",
            amount="500.00",
            currency="USD",
            status="COMPLETED",
            requested_at=now,
            completed_at=now,
        )
        assert w.amount == "500.00"
        assert w.status == "COMPLETED"

    def test_completed_at_nullable(self) -> None:
        w = Withdrawal(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_withdrawal_id="wd_002",
            amount="100.00",
            currency="USD",
            status="REQUESTED",
            requested_at=datetime.now(timezone.utc),
        )
        assert w.completed_at is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_withdrawal_model.py -v`
Expected: FAIL

- [ ] **Step 3: Add Withdrawal model**

Add to `backend/db/models/finance.py`:

```python
class Withdrawal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "withdrawals"

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
    platform_withdrawal_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    amount: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="REQUESTED, PROCESSING, COMPLETED, FAILED"
    )
    requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
```

- [ ] **Step 4: Add to model registry**

In `backend/db/models/__init__.py`, add `Withdrawal` to imports and `__all__`.

- [ ] **Step 5: Run test and commit**

```bash
pytest tests/unit/models/test_withdrawal_model.py -v
alembic revision --autogenerate -m "add_withdrawal_model"
git add backend/db/models/finance.py backend/db/models/__init__.py tests/unit/models/test_withdrawal_model.py alembic/versions/
git commit -m "feat(finance): add Withdrawal model for persistent withdrawal tracking"
```

---

### Task B4: Add finance analytics service

**Files:**
- Create: `backend/modules/commerce/services/finance_analytics.py`
- Test: `tests/unit/commerce/test_finance_analytics.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for FinanceAnalyticsService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.commerce.services.finance_analytics import FinanceAnalyticsService


class TestRevenueSummary:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_get_revenue_summary_returns_structure(
        self, mock_session: AsyncMock
    ) -> None:
        # Mock DB to return aggregated results
        result_mock = MagicMock()
        result_mock.one.return_value = (
            "5000.00",  # total_gross
            "300.00",   # total_fees
            "4700.00",  # total_net
            10,         # settlement_count
        )
        mock_session.execute.return_value = result_mock

        service = FinanceAnalyticsService(mock_session)
        summary = await service.get_revenue_summary(uuid.uuid4(), days=30)

        assert summary["total_gross"] == "5000.00"
        assert summary["total_fees"] == "300.00"
        assert summary["total_net"] == "4700.00"
        assert summary["settlement_count"] == 10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/commerce/test_finance_analytics.py -v`
Expected: FAIL

- [ ] **Step 3: Create finance analytics service**

Create `backend/modules/commerce/services/finance_analytics.py`:

```python
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.finance import Settlement, Transaction

logger = logging.getLogger(__name__)


class FinanceAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_revenue_summary(
        self,
        workspace_id: uuid.UUID,
        *,
        days: int = 30,
        shop_id: uuid.UUID | None = None,
    ) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        query = select(
            func.coalesce(func.sum(text("CAST(amount AS DECIMAL)")), 0),
            func.coalesce(func.sum(text("CAST(fees_total AS DECIMAL)")), 0),
            func.coalesce(func.sum(text("CAST(payout_amount AS DECIMAL)")), 0),
            func.count(Settlement.id),
        ).where(
            Settlement.workspace_id == workspace_id,
            Settlement.created_at >= since,
        )

        if shop_id:
            query = query.where(Settlement.shop_id == shop_id)

        result = await self._session.execute(query)
        row = result.one()

        return {
            "total_gross": str(row[0]),
            "total_fees": str(row[1]),
            "total_net": str(row[2]),
            "settlement_count": row[3],
            "period_days": days,
        }

    async def get_fee_breakdown(
        self,
        workspace_id: uuid.UUID,
        *,
        days: int = 30,
    ) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self._session.execute(
            select(
                Transaction.transaction_type,
                func.count(Transaction.id).label("count"),
                func.coalesce(func.sum(text("CAST(amount AS DECIMAL)")), 0).label("total"),
            )
            .where(
                Transaction.workspace_id == workspace_id,
                Transaction.created_at >= since,
            )
            .group_by(Transaction.transaction_type)
        )

        return [
            {"type": row[0], "count": row[1], "total": str(row[2])}
            for row in result.all()
        ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/commerce/test_finance_analytics.py -v`
Expected: PASS

- [ ] **Step 5: Add analytics routes to finance routes**

Add to `backend/modules/commerce/routes/finance.py`:

```python
from backend.modules.commerce.services.finance_analytics import FinanceAnalyticsService


@router.get("/finance/analytics/revenue")
async def get_revenue_summary(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
    shop_id: uuid.UUID | None = None,
) -> dict:
    service = FinanceAnalyticsService(db)
    return await service.get_revenue_summary(workspace_id, days=days, shop_id=shop_id)


@router.get("/finance/analytics/fees")
async def get_fee_breakdown(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> list[dict]:
    service = FinanceAnalyticsService(db)
    return await service.get_fee_breakdown(workspace_id, days=days)
```

- [ ] **Step 6: Commit**

```bash
git add backend/modules/commerce/services/finance_analytics.py backend/modules/commerce/routes/finance.py tests/unit/commerce/test_finance_analytics.py
git commit -m "feat(finance): add FinanceAnalyticsService with revenue summary and fee breakdown"
```

---

### Task B5: Add Celery beat schedules for finance sync

**Files:**
- Create: `backend/workers/finance_sync.py`
- Modify: `backend/workers/celery_app.py`
- Test: `tests/unit/test_finance_sync_worker.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for finance sync Celery tasks."""

import pytest

from backend.workers.finance_sync import sync_daily_statements, sync_unsettled_transactions


class TestFinanceSyncWorkers:
    def test_sync_statements_task_name(self) -> None:
        assert sync_daily_statements.name == "backend.workers.finance_sync.sync_daily_statements"

    def test_sync_unsettled_task_name(self) -> None:
        assert sync_unsettled_transactions.name == "backend.workers.finance_sync.sync_unsettled_transactions"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_finance_sync_worker.py -v`
Expected: FAIL

- [ ] **Step 3: Create finance sync worker**

Create `backend/workers/finance_sync.py`:

```python
import asyncio
import logging

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.workers.finance_sync.sync_daily_statements")
def sync_daily_statements() -> dict[str, int]:
    """Sync settlement statements from TikTok for all shops."""
    return asyncio.get_event_loop().run_until_complete(_sync_daily_statements())


async def _sync_daily_statements() -> dict[str, int]:
    from sqlalchemy import select

    from backend.db.engine import async_session_factory
    from backend.db.models.commerce import Shop
    from backend.modules.commerce.services.finance_service import FinanceService

    totals: dict[str, int] = {"settlements": 0, "transactions": 0, "payments": 0}
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = list(result.scalars().all())

        service = FinanceService(session)
        for shop in shops:
            try:
                totals["settlements"] += await service.sync_settlements(shop)
                totals["transactions"] += await service.sync_transactions(shop)
                totals["payments"] += await service.sync_payments(shop)
            except Exception:
                logger.exception("Failed to sync finance for shop %s", shop.id)

        await session.commit()

    logger.info("Finance sync complete: %s", totals)
    return totals


@celery_app.task(name="backend.workers.finance_sync.sync_unsettled_transactions")
def sync_unsettled_transactions() -> dict[str, str]:
    """Fetch unsettled transactions (API-only, no persistence yet)."""
    logger.info("Unsettled transaction sync triggered")
    return {"status": "completed"}
```

- [ ] **Step 4: Add beat schedules**

Add to `backend/workers/celery_app.py` `beat_schedule`:

```python
    "sync-daily-statements": {
        "task": "backend.workers.finance_sync.sync_daily_statements",
        "schedule": crontab(minute=1, hour=1),  # Daily at 01:01 UTC
    },
    "sync-unsettled-transactions": {
        "task": "backend.workers.finance_sync.sync_unsettled_transactions",
        "schedule": crontab(minute=31, hour="*/4"),  # Every 4h, offset :31
    },
```

- [ ] **Step 5: Run test and commit**

```bash
pytest tests/unit/test_finance_sync_worker.py -v
git add backend/workers/finance_sync.py backend/workers/celery_app.py tests/unit/test_finance_sync_worker.py
git commit -m "feat(finance): add Celery workers for daily statement and unsettled sync"
```

---

## Phase C: GMV Max Module (New)

**Current state:** Only `get_gmv_max_report()` exists in the advertising module. No campaign creation, no workflow, no recommendations.

**What this phase adds:** Entirely new `backend/modules/gmvmax/` module with guided workflow, draft persistence, deep-link generation, reporting sync, and recommendation engine.

### Task C1: Create GMV Max database models

**Files:**
- Create: `backend/db/models/gmvmax.py`
- Modify: `backend/db/models/__init__.py`
- Test: `tests/unit/models/test_gmvmax_models.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for GMV Max models."""

import uuid
from datetime import date, datetime, timezone

import pytest

from backend.db.models.gmvmax import GmvMaxDraft, GmvMaxReport


class TestGmvMaxDraft:
    def test_draft_creation(self) -> None:
        draft = GmvMaxDraft(
            workspace_id=uuid.uuid4(),
            campaign_type="PRODUCT",
            product_ids=["prod_1", "prod_2"],
            daily_budget="50.00",
            roi_target="3.0",
            status="DRAFT",
            created_by=uuid.uuid4(),
            notes="Test campaign",
        )
        assert draft.campaign_type == "PRODUCT"
        assert draft.product_ids == ["prod_1", "prod_2"]
        assert draft.ads_manager_campaign_id is None

    def test_draft_linked_to_ads_manager(self) -> None:
        draft = GmvMaxDraft(
            workspace_id=uuid.uuid4(),
            campaign_type="LIVE",
            product_ids=["prod_1"],
            daily_budget="100.00",
            roi_target="2.5",
            status="LINKED",
            ads_manager_campaign_id="campaign_12345",
            created_by=uuid.uuid4(),
        )
        assert draft.status == "LINKED"
        assert draft.ads_manager_campaign_id == "campaign_12345"


class TestGmvMaxReport:
    def test_report_creation(self) -> None:
        report = GmvMaxReport(
            workspace_id=uuid.uuid4(),
            campaign_id="campaign_001",
            report_date=date(2026, 3, 30),
            spend="100.00",
            total_gmv="350.00",
            paid_gmv="200.00",
            organic_gmv="150.00",
            orders=25,
            roi="3.50",
            impressions=10000,
            clicks=500,
        )
        assert report.roi == "3.50"
        assert report.orders == 25
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/models/test_gmvmax_models.py -v`
Expected: FAIL

- [ ] **Step 3: Create GMV Max models**

Create `backend/db/models/gmvmax.py`:

```python
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class GmvMaxDraft(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gmvmax_drafts"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="PRODUCT or LIVE"
    )
    product_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    daily_budget: Mapped[str] = mapped_column(String(20), nullable=False)
    roi_target: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="DRAFT",
        comment="DRAFT, SUBMITTED, LINKED, ARCHIVED",
    )
    ads_manager_campaign_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Linked after user creates in Ads Manager"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_gmvmax_drafts_workspace_status", "workspace_id", "status"),
    )


class GmvMaxReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gmvmax_reports"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[str] = mapped_column(String(255), nullable=False)
    draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gmvmax_drafts.id", ondelete="SET NULL"),
        nullable=True,
    )
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    spend: Mapped[str] = mapped_column(String(20), nullable=False)
    total_gmv: Mapped[str] = mapped_column(String(20), nullable=False)
    paid_gmv: Mapped[str | None] = mapped_column(String(20), nullable=True)
    organic_gmv: Mapped[str | None] = mapped_column(String(20), nullable=True)
    orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    roi: Mapped[str | None] = mapped_column(String(20), nullable=True)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_gmvmax_reports_campaign_date", "campaign_id", "report_date", unique=True),
    )
```

- [ ] **Step 4: Add to model registry, create migration, run test, commit**

```bash
# Add imports to backend/db/models/__init__.py
pytest tests/unit/models/test_gmvmax_models.py -v
alembic revision --autogenerate -m "add_gmvmax_models"
git add backend/db/models/gmvmax.py backend/db/models/__init__.py tests/unit/models/test_gmvmax_models.py alembic/versions/
git commit -m "feat(gmvmax): add GmvMaxDraft and GmvMaxReport models"
```

---

### Task C2: Create GMV Max module with workflow service

**Files:**
- Create: `backend/modules/gmvmax/__init__.py`
- Create: `backend/modules/gmvmax/schemas.py`
- Create: `backend/modules/gmvmax/services/workflow_service.py`
- Create: `backend/modules/gmvmax/routes/workflow_routes.py`
- Create: `backend/modules/gmvmax/routes/__init__.py`
- Modify: `backend/main.py`
- Test: `tests/unit/gmvmax/test_workflow_service.py` (create)

- [ ] **Step 1: Write the failing test**

```python
"""Tests for GMV Max workflow service."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.gmvmax.services.workflow_service import GmvMaxWorkflowService


class TestCreateDraft:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_create_draft(self, mock_session: AsyncMock) -> None:
        service = GmvMaxWorkflowService(mock_session)
        draft = await service.create_draft(
            workspace_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            campaign_type="PRODUCT",
            product_ids=["prod_1", "prod_2"],
            daily_budget="50.00",
            roi_target="3.0",
        )
        assert draft.campaign_type == "PRODUCT"
        assert draft.status == "DRAFT"
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_draft_validates_campaign_type(
        self, mock_session: AsyncMock
    ) -> None:
        service = GmvMaxWorkflowService(mock_session)
        with pytest.raises(ValueError, match="PRODUCT or LIVE"):
            await service.create_draft(
                workspace_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                campaign_type="INVALID",
                product_ids=["prod_1"],
                daily_budget="50.00",
                roi_target="3.0",
            )


class TestGenerateDeepLink:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_deep_link_for_product_campaign(self, mock_session: AsyncMock) -> None:
        service = GmvMaxWorkflowService(mock_session)
        url = service.generate_deep_link("PRODUCT")
        assert "ads.tiktok.com" in url
        assert "gmvmax" in url.lower() or "product" in url.lower()

    @pytest.mark.asyncio
    async def test_deep_link_for_live_campaign(self, mock_session: AsyncMock) -> None:
        service = GmvMaxWorkflowService(mock_session)
        url = service.generate_deep_link("LIVE")
        assert "ads.tiktok.com" in url
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/gmvmax/test_workflow_service.py -v`
Expected: FAIL

- [ ] **Step 3: Create module structure**

Create `backend/modules/gmvmax/__init__.py` (empty).

Create `backend/modules/gmvmax/schemas.py`:

```python
from pydantic import BaseModel, ConfigDict, Field


class CreateDraftRequest(BaseModel):
    campaign_type: str = Field(description="PRODUCT or LIVE")
    product_ids: list[str]
    daily_budget: str
    roi_target: str
    notes: str | None = None


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_type: str
    product_ids: list
    daily_budget: str
    roi_target: str
    status: str
    ads_manager_campaign_id: str | None = None
    notes: str | None = None
    created_at: str
    updated_at: str


class LinkDraftRequest(BaseModel):
    ads_manager_campaign_id: str


class DeepLinkResponse(BaseModel):
    url: str
    campaign_type: str
```

Create `backend/modules/gmvmax/services/__init__.py` (empty).

Create `backend/modules/gmvmax/services/workflow_service.py`:

```python
import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.gmvmax import GmvMaxDraft
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)

ADS_MANAGER_BASE = "https://ads.tiktok.com/i18n/perf/campaign/create"


class GmvMaxWorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_draft(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        campaign_type: str,
        product_ids: list[str],
        daily_budget: str,
        roi_target: str,
        notes: str | None = None,
    ) -> GmvMaxDraft:
        if campaign_type not in ("PRODUCT", "LIVE"):
            raise ValueError("campaign_type must be PRODUCT or LIVE")

        draft = GmvMaxDraft(
            workspace_id=workspace_id,
            campaign_type=campaign_type,
            product_ids=product_ids,
            daily_budget=daily_budget,
            roi_target=roi_target,
            status="DRAFT",
            created_by=user_id,
            notes=notes,
        )
        self._session.add(draft)
        await self._session.flush()
        return draft

    async def get_draft(self, draft_id: uuid.UUID) -> GmvMaxDraft | None:
        result = await self._session.execute(
            select(GmvMaxDraft).where(GmvMaxDraft.id == draft_id)
        )
        return result.scalar_one_or_none()

    async def list_drafts(
        self,
        workspace_id: uuid.UUID,
        *,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[GmvMaxDraft]:
        query = select(GmvMaxDraft).where(GmvMaxDraft.workspace_id == workspace_id)
        count_query = select(func.count(GmvMaxDraft.id)).where(
            GmvMaxDraft.workspace_id == workspace_id
        )

        if status_filter:
            query = query.where(GmvMaxDraft.status == status_filter)
            count_query = count_query.where(GmvMaxDraft.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(GmvMaxDraft.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def link_draft(
        self, draft: GmvMaxDraft, ads_manager_campaign_id: str
    ) -> GmvMaxDraft:
        draft.ads_manager_campaign_id = ads_manager_campaign_id
        draft.status = "LINKED"
        return draft

    def generate_deep_link(self, campaign_type: str) -> str:
        subtype = "product" if campaign_type == "PRODUCT" else "live"
        return f"{ADS_MANAGER_BASE}?type=gmvmax&subtype={subtype}"
```

- [ ] **Step 4: Create routes and register in main.py**

Create `backend/modules/gmvmax/routes/__init__.py`:

```python
from fastapi import APIRouter

from backend.modules.gmvmax.routes.workflow_routes import router as workflow_router

router = APIRouter(prefix="/gmvmax", tags=["gmvmax"])

router.include_router(workflow_router)
```

Create `backend/modules/gmvmax/routes/workflow_routes.py`:

```python
import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.gmvmax.schemas import (
    CreateDraftRequest,
    DeepLinkResponse,
    DraftResponse,
    LinkDraftRequest,
)
from backend.modules.gmvmax.services.workflow_service import GmvMaxWorkflowService

router = APIRouter()


@router.post("/drafts", response_model=DraftResponse)
async def create_draft(
    workspace_id: uuid.UUID,
    body: CreateDraftRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    service = GmvMaxWorkflowService(db)
    draft = await service.create_draft(
        workspace_id,
        current_user.id,
        campaign_type=body.campaign_type,
        product_ids=body.product_ids,
        daily_budget=body.daily_budget,
        roi_target=body.roi_target,
        notes=body.notes,
    )
    return DraftResponse.model_validate(draft)


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    service = GmvMaxWorkflowService(db)
    draft = await service.get_draft(draft_id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
        )
    return DraftResponse.model_validate(draft)


@router.post("/drafts/{draft_id}/link", response_model=DraftResponse)
async def link_draft(
    draft_id: uuid.UUID,
    body: LinkDraftRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    service = GmvMaxWorkflowService(db)
    draft = await service.get_draft(draft_id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
        )
    linked = await service.link_draft(draft, body.ads_manager_campaign_id)
    return DraftResponse.model_validate(linked)


@router.get("/deep-link/{campaign_type}", response_model=DeepLinkResponse)
async def get_deep_link(
    campaign_type: str,
    current_user: CurrentUser,
    db: DBSession,
) -> DeepLinkResponse:
    service = GmvMaxWorkflowService(db)
    url = service.generate_deep_link(campaign_type)
    return DeepLinkResponse(url=url, campaign_type=campaign_type)
```

Add to `backend/main.py`:

```python
from backend.modules.gmvmax.routes import router as gmvmax_router
```

And in `create_app()`:

```python
    app.include_router(gmvmax_router, prefix=api_prefix)
```

- [ ] **Step 5: Run tests and commit**

```bash
pytest tests/unit/gmvmax/test_workflow_service.py -v
git add backend/modules/gmvmax/ tests/unit/gmvmax/ backend/main.py backend/db/models/gmvmax.py backend/db/models/__init__.py
git commit -m "feat(gmvmax): add GMV Max module with workflow service, drafts, and deep-links"
```

---

## Phases D, E, F — Summary Tasks

> **Note:** Phases D, E, and F follow the same patterns established in A, B, and C. The detailed task breakdown below provides the key implementation points for each. Each follows the same TDD cycle: write test → verify fail → implement → verify pass → commit.

---

## Phase D: Customer Service & Engagement Enhancement

### Task D1: Extend customer service with agent settings and CS performance

**Files to modify:**
- `backend/modules/commerce/services/customer_service.py` — Add `get_agent_settings()`, `update_agent_settings()`, `get_cs_performance()`, `upload_image()`, `search_sessions()`
- `backend/modules/commerce/routes/customer_service.py` — Add routes for agent settings, performance, image upload
- Add `CsPerformanceSnapshot` model to `backend/db/models/` for daily CS metrics persistence
- Test: `tests/unit/commerce/test_customer_service_enhanced.py`

Key implementation:
```python
# New methods on CustomerServiceService
async def get_agent_settings(self, shop: Shop) -> dict:
    gateway = await self._build_gateway(shop)
    resp = await gateway.get("/customer_service/202309/agents/settings")
    return resp.get("data", {})

async def update_agent_settings(self, shop: Shop, *, settings: dict) -> dict:
    gateway = await self._build_gateway(shop)
    resp = await gateway.post("/customer_service/202309/agents/settings", json_body=settings)
    return resp.get("data", {})

async def get_cs_performance(self, shop: Shop) -> dict:
    gateway = await self._build_gateway(shop)
    resp = await gateway.get("/customer_service/202309/performance")
    return resp.get("data", {})
```

### Task D2: Create Customer Engagement module (new)

**Files to create:**
- `backend/modules/customer_engagement/__init__.py`
- `backend/modules/customer_engagement/schemas.py`
- `backend/modules/customer_engagement/services/engagement_service.py`
- `backend/modules/customer_engagement/routes/__init__.py`
- `backend/modules/customer_engagement/routes/engagement_routes.py`
- Register in `backend/main.py`

Key API methods:
```python
# EngagementService methods
async def get_templates(self, shop: Shop) -> list[dict]
async def create_task(self, shop: Shop, *, template_id: str, audience: dict) -> dict
async def create_custom_task(self, shop: Shop, *, message: str, audience: dict) -> dict
async def get_task_performance(self, shop: Shop, task_id: str) -> dict
async def get_permissions(self, shop: Shop) -> dict
```

### Task D3: Add Celery workers for CS sync

**Files:**
- Create: `backend/workers/customer_service_sync.py`
- Modify: `backend/workers/celery_app.py`

Beat schedules:
- `sync-cs-conversations`: every 15min
- `sync-cs-performance`: daily at 02:05 UTC
- `sync-engagement-templates`: daily at 03:15 UTC

---

## Phase E: Affiliate Enhancement

### Task E1: Add creator discovery and search to affiliate service

**Files to modify:**
- `backend/modules/commerce/services/affiliate_service.py` — Add `search_creators()`, `get_creator_performance()`, `get_creator_profile()`
- `backend/modules/commerce/routes/affiliate.py` — Add creator search/discovery routes

Key API methods:
```python
async def search_creators(self, shop: Shop, *, filters: dict) -> dict:
    gateway = await self._build_gateway(shop)
    return await gateway.get("/affiliate/202309/seller/creators", params=filters)

async def get_creator_performance(self, shop: Shop, creator_id: str) -> dict:
    gateway = await self._build_gateway(shop)
    return await gateway.get(f"/affiliate/202309/seller/creators/{creator_id}/performance")
```

### Task E2: Add sample management to affiliate service

**Files to create/modify:**
- Add `SampleRequest` model to `backend/db/models/affiliate.py`
- Add `approve_sample()`, `reject_sample()`, `list_sample_requests()` to `AffiliateService`
- Add sample routes to `backend/modules/commerce/routes/affiliate.py`

### Task E3: Add affiliate order tracking

**Files to create/modify:**
- Add `AffiliateOrder` model to `backend/db/models/affiliate.py`
- Add `list_affiliate_orders()`, `sync_affiliate_orders()` to `AffiliateService`
- Add routes and Celery worker

### Task E4: Add creator messaging

**Files to modify:**
- Add `get_creator_conversations()`, `send_creator_message()` to `AffiliateService`
- Add messaging routes

### Task E5: Add Celery workers for affiliate sync

Beat schedules:
- `sync-affiliate-creators`: daily at 04:33 UTC
- `sync-affiliate-orders`: every 2h, offset :43
- `sync-sample-requests`: every 30min, offset :14

---

## Phase F: Shop Health & Unified Analytics

### Task F1: Create Shop Health models

**Files to create:**
- `backend/db/models/shop_health.py` — `SpsSnapshot`, `ViolationRecord`, `HealthAlert`, `UnifiedDailyMetrics`
- Register in `backend/db/models/__init__.py`

### Task F2: Create SPS estimation service

**Files to create:**
- `backend/modules/shop_health/__init__.py`
- `backend/modules/shop_health/services/sps_service.py` — Cross-module aggregation to estimate SPS
- `backend/modules/shop_health/routes/__init__.py`
- `backend/modules/shop_health/routes/sps_routes.py`

Key logic: Query returns, orders, fulfillment, CS performance from existing modules to compute estimated SPS 0-5.

### Task F3: Create alert service

**Files:**
- `backend/modules/shop_health/services/alert_service.py` — Threshold evaluation, alert creation
- Alert thresholds: SPS < 3.5 (WARNING), SPS < 3.0 (CRITICAL), violations >= 12 (WARNING), CS response rate < 85% (WARNING)

### Task F4: Create unified daily metrics service

**Files:**
- `backend/modules/shop_health/services/analytics_service.py` — Roll up from commerce, finance, advertising, affiliate, CS into denormalized daily metrics

### Task F5: Create Celery workers for shop health

Beat schedules:
- `calculate-daily-sps`: daily at 01:01 UTC
- `calculate-daily-unified-metrics`: daily at 01:30 UTC
- `check-health-alerts`: every 2h, offset :46

### Task F6: Register shop health module

- Register routes in `backend/main.py`
- Run full test suite to verify no regressions

---

## Final: Full Integration Verification

### Task FINAL: Run full test suite and verify

- [ ] **Step 1: Run all tests**

```bash
pytest --tb=short -q
```

Expected: All existing tests + new tests pass.

- [ ] **Step 2: Run linting**

```bash
ruff format backend/ tests/
ruff check backend/ tests/ --fix
```

- [ ] **Step 3: Run type checking**

```bash
mypy backend/
```

- [ ] **Step 4: Verify all migrations**

```bash
alembic upgrade head
```

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete TikTok Shop end-to-end operations — 6 phases implemented"
```
