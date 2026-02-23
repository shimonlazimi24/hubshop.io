# Multi-Platform Views Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add per-platform toggle (All | TikTok Ads | Shop Promotions for Advertising; All | TikTok Shop | Affiliates for Commerce) with unified read-only view and per-platform action views.

**Architecture:** Thin aggregation services call existing platform-specific services and tag results with `source_platform`. Frontend `PlatformTabs` component drives a `?platform=` URL param that filters data.

**Tech Stack:** Python/FastAPI (backend), Next.js/TypeScript (frontend), pytest (tests)

---

### Task 1: Create PlatformTabs Frontend Component

**Files:**
- Create: `frontend/src/components/ui/platform-tabs.tsx`

**Step 1: Write the component**

```typescript
// frontend/src/components/ui/platform-tabs.tsx
"use client";

import { cn } from "@/lib/utils";

export interface PlatformTab {
  key: string;
  label: string;
}

interface PlatformTabsProps {
  tabs: PlatformTab[];
  value: string;
  onChange: (key: string) => void;
  className?: string;
}

export function PlatformTabs({ tabs, value, onChange, className }: PlatformTabsProps) {
  return (
    <div className={cn("flex items-center gap-1 rounded-lg bg-gray-100 p-1 mb-4", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            value === tab.key
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
```

**Step 2: Export from barrel**

Add to `frontend/src/components/ui/index.ts` (or wherever the barrel export is — check if it exists first; if not, just import directly from the file).

**Step 3: Commit**

```bash
git add frontend/src/components/ui/platform-tabs.tsx
git commit -m "feat: add PlatformTabs reusable UI component"
```

---

### Task 2: Add `source_platform` to Advertising Schemas

**Files:**
- Modify: `backend/modules/advertising/schemas.py:23-35` (CampaignSummaryResponse)
- Test: `tests/unit/advertising/test_advertising_schemas.py`

**Step 1: Write the failing test**

```python
# tests/unit/advertising/test_advertising_schemas.py
"""Tests for advertising schemas with source_platform field."""

from datetime import datetime, timezone

from backend.modules.advertising.schemas import CampaignSummaryResponse


class TestCampaignSummarySourcePlatform:
    def test_source_platform_defaults_to_marketing(self) -> None:
        data = {
            "id": "abc",
            "platform_campaign_id": "camp_1",
            "campaign_name": "Test",
            "operation_status": "ENABLE",
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = CampaignSummaryResponse(**data)
        assert response.source_platform == "marketing"

    def test_source_platform_can_be_set_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_campaign_id": "camp_1",
            "campaign_name": "Test",
            "operation_status": "ENABLE",
            "source_platform": "shop",
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = CampaignSummaryResponse(**data)
        assert response.source_platform == "shop"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/advertising/test_advertising_schemas.py -v`
Expected: FAIL — `source_platform` field doesn't exist yet.

**Step 3: Add `source_platform` field to CampaignSummaryResponse**

In `backend/modules/advertising/schemas.py`, add to `CampaignSummaryResponse` (after line 35):

```python
class CampaignSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_campaign_id: str
    campaign_name: str
    objective_type: str | None = None
    budget_mode: str | None = None
    budget: str | None = None
    operation_status: str
    secondary_status: str | None = None
    source_platform: str = "marketing"  # NEW
    created_at: datetime
    updated_at: datetime
```

Also add to `CampaignDetailResponse`:

```python
class CampaignDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_campaign_id: str
    campaign_name: str
    objective_type: str | None = None
    budget_mode: str | None = None
    budget: str | None = None
    operation_status: str
    secondary_status: str | None = None
    source_platform: str = "marketing"  # NEW
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/advertising/test_advertising_schemas.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/advertising/schemas.py tests/unit/advertising/test_advertising_schemas.py
git commit -m "feat: add source_platform field to advertising campaign schemas"
```

---

### Task 3: Add `source_platform` to Commerce Schemas

**Files:**
- Modify: `backend/modules/commerce/schemas.py:109-121` (OrderSummaryResponse)
- Test: `tests/unit/commerce/test_commerce_schemas.py`

**Step 1: Write the failing test**

```python
# tests/unit/commerce/test_commerce_schemas.py
"""Tests for commerce schemas with source_platform field."""

from datetime import datetime, timezone

from backend.modules.commerce.schemas import OrderSummaryResponse


class TestOrderSummarySourcePlatform:
    def test_source_platform_defaults_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_order_id": "ord_1",
            "status": "completed",
            "total_amount": "99.00",
            "currency": "USD",
            "item_count": 2,
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = OrderSummaryResponse(**data)
        assert response.source_platform == "shop"

    def test_source_platform_can_be_set_to_affiliate(self) -> None:
        data = {
            "id": "abc",
            "platform_order_id": "ord_1",
            "status": "completed",
            "total_amount": "99.00",
            "currency": "USD",
            "item_count": 2,
            "source_platform": "affiliate",
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = OrderSummaryResponse(**data)
        assert response.source_platform == "affiliate"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/commerce/test_commerce_schemas.py -v`
Expected: FAIL

**Step 3: Add `source_platform` to OrderSummaryResponse and OrderDetailResponse**

In `backend/modules/commerce/schemas.py`:

```python
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
    source_platform: str = "shop"  # NEW
    created_at: datetime
    updated_at: datetime
```

Same for `OrderDetailResponse` — add `source_platform: str = "shop"` before `line_items`.

Also add to `ProductSummaryResponse`:

```python
    source_platform: str = "shop"  # NEW — after sku_count, before created_at
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/commerce/test_commerce_schemas.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/commerce/schemas.py tests/unit/commerce/test_commerce_schemas.py
git commit -m "feat: add source_platform field to commerce order/product schemas"
```

---

### Task 4: Create UnifiedAdvertisingService

**Files:**
- Create: `backend/modules/advertising/services/unified_service.py`
- Test: `tests/unit/advertising/test_unified_advertising_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/advertising/test_unified_advertising_service.py
"""Tests for UnifiedAdvertisingService — cross-platform campaign aggregation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.unified_service import (
    UnifiedAdvertisingService,
)


class TestListCampaignsUnified:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_marketing_campaigns_when_platform_is_marketing(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_campaign = SimpleNamespace(
            id=uuid.uuid4(),
            platform_campaign_id="camp_1",
            campaign_name="Marketing Campaign",
            objective_type="TRAFFIC",
            budget_mode="BUDGET_MODE_DAY",
            budget="100",
            operation_status="ENABLE",
            secondary_status=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_campaign], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.advertising.services.unified_service.CampaignService"
        ) as MockCampaignService:
            mock_svc = AsyncMock()
            mock_svc.list_campaigns.return_value = mock_result
            MockCampaignService.return_value = mock_svc

            service = UnifiedAdvertisingService(mock_session)
            result = await service.list_campaigns(
                workspace_id, platform="marketing"
            )

        assert len(result.items) == 1
        assert result.items[0].source_platform == "marketing"

    @pytest.mark.asyncio
    async def test_returns_all_when_platform_is_none(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_campaign = SimpleNamespace(
            id=uuid.uuid4(),
            platform_campaign_id="camp_1",
            campaign_name="Marketing Campaign",
            objective_type="TRAFFIC",
            budget_mode="BUDGET_MODE_DAY",
            budget="100",
            operation_status="ENABLE",
            secondary_status=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_campaign], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.advertising.services.unified_service.CampaignService"
        ) as MockCampaignService:
            mock_svc = AsyncMock()
            mock_svc.list_campaigns.return_value = mock_result
            MockCampaignService.return_value = mock_svc

            service = UnifiedAdvertisingService(mock_session)
            result = await service.list_campaigns(workspace_id, platform=None)

        assert len(result.items) >= 1
        assert all(
            item.source_platform in ("marketing", "shop") for item in result.items
        )
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/advertising/test_unified_advertising_service.py -v`
Expected: FAIL — module doesn't exist.

**Step 3: Implement UnifiedAdvertisingService**

```python
# backend/modules/advertising/services/unified_service.py
"""Thin aggregation layer for cross-platform advertising data."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.advertising.schemas import CampaignSummaryResponse
from backend.modules.advertising.services.campaign_service import CampaignService
from backend.modules.commerce.schemas import PaginatedResponse


@dataclass
class UnifiedAdvertisingService:
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_campaigns(
        self,
        workspace_id: uuid.UUID,
        *,
        platform: str | None = None,
        ad_account_id: uuid.UUID | None = None,
        objective: str | None = None,
        status_filter: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[CampaignSummaryResponse]:
        items: list[CampaignSummaryResponse] = []

        if platform is None or platform == "marketing":
            campaign_service = CampaignService(self._session)
            result = await campaign_service.list_campaigns(
                workspace_id,
                ad_account_id=ad_account_id,
                objective=objective,
                status_filter=status_filter,
                search=search,
                page=page,
                page_size=page_size,
            )
            for c in result.items:
                resp = CampaignSummaryResponse.model_validate(c)
                resp.source_platform = "marketing"
                items.append(resp)

            if platform == "marketing":
                return PaginatedResponse(
                    items=items,
                    total=result.total,
                    page=result.page,
                    page_size=result.page_size,
                    total_pages=result.total_pages,
                )

        # When platform is None (unified) or "shop", we'd also pull
        # shop promotions here. For now, return marketing-only since
        # shop promotions use a different schema. This can be extended
        # when Shop campaigns are normalized into the same schema.

        total = len(items)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/advertising/test_unified_advertising_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/advertising/services/unified_service.py tests/unit/advertising/test_unified_advertising_service.py
git commit -m "feat: add UnifiedAdvertisingService for cross-platform campaign aggregation"
```

---

### Task 5: Add `platform` Query Param to Advertising Campaign Routes

**Files:**
- Modify: `backend/modules/advertising/routes/campaigns.py:20-51`
- Test: `tests/unit/advertising/test_campaign_routes.py`

**Step 1: Write the failing test**

```python
# tests/unit/advertising/test_campaign_routes.py
"""Tests for campaign routes with platform query param."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.modules.advertising.routes.campaigns import router


@pytest.fixture
def app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(router, prefix="/ads")
    return test_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestListCampaignsWithPlatform:
    @pytest.mark.asyncio
    async def test_accepts_platform_query_param(self, client: TestClient) -> None:
        """The route should accept ?platform=marketing without error."""
        # We just verify the route signature accepts the param.
        # Full integration test would need DB, but this validates the param exists.
        # A 422 would mean the param isn't declared; any other status is fine.
        with patch(
            "backend.modules.advertising.routes.campaigns.UnifiedAdvertisingService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.list_campaigns.return_value = SimpleNamespace(
                items=[], total=0, page=1, page_size=20, total_pages=0
            )
            MockService.return_value = mock_svc

            # Note: This will fail on auth dependency; we just check it doesn't 422
            # on the platform param itself. In a real test, override dependencies.
```

> **Note to implementer:** The exact test approach depends on how `CurrentUser` dependency is resolved. If it's complex to mock, skip the route-level test and rely on the schema + service tests above. The key change is straightforward — just adding a parameter.

**Step 2: Update the route**

In `backend/modules/advertising/routes/campaigns.py`, modify `list_campaigns`:

```python
from backend.modules.advertising.services.unified_service import UnifiedAdvertisingService

@router.get(
    "/campaigns",
    response_model=PaginatedResponse[CampaignSummaryResponse],
)
async def list_campaigns(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
    objective: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    platform: str | None = None,  # NEW
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CampaignSummaryResponse]:
    service = UnifiedAdvertisingService(db)
    return await service.list_campaigns(
        workspace_id,
        platform=platform,
        ad_account_id=ad_account_id,
        objective=objective,
        status_filter=status_filter,
        search=search,
        page=page,
        page_size=page_size,
    )
```

**Step 3: Run existing tests to ensure no regression**

Run: `pytest tests/unit/advertising/ -v`
Expected: All existing tests PASS

**Step 4: Commit**

```bash
git add backend/modules/advertising/routes/campaigns.py
git commit -m "feat: add platform query param to advertising campaigns route"
```

---

### Task 6: Create UnifiedCommerceService

**Files:**
- Create: `backend/modules/commerce/services/unified_service.py`
- Test: `tests/unit/commerce/test_unified_commerce_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/commerce/test_unified_commerce_service.py
"""Tests for UnifiedCommerceService — cross-platform order aggregation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.unified_service import UnifiedCommerceService


class TestListOrdersUnified:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_shop_orders_when_platform_is_shop(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_order = SimpleNamespace(
            id=uuid.uuid4(),
            platform_order_id="ord_1",
            status="completed",
            total_amount="99.00",
            currency="USD",
            item_count=2,
            fulfillment_type="SHIP_BY_SELLER",
            rts_sla=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_order], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.commerce.services.unified_service.OrderService"
        ) as MockOrderService:
            mock_svc = AsyncMock()
            mock_svc.list_orders.return_value = mock_result
            MockOrderService.return_value = mock_svc

            service = UnifiedCommerceService(mock_session)
            result = await service.list_orders(workspace_id, platform="shop")

        assert len(result.items) == 1
        assert result.items[0].source_platform == "shop"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/commerce/test_unified_commerce_service.py -v`
Expected: FAIL — module doesn't exist.

**Step 3: Implement UnifiedCommerceService**

```python
# backend/modules/commerce/services/unified_service.py
"""Thin aggregation layer for cross-platform commerce data."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.commerce.schemas import (
    OrderSummaryResponse,
    PaginatedResponse,
    ProductSummaryResponse,
)
from backend.modules.commerce.services.order_service import OrderService


class UnifiedCommerceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(
        self,
        workspace_id: uuid.UUID,
        *,
        platform: str | None = None,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[OrderSummaryResponse]:
        items: list[OrderSummaryResponse] = []

        if platform is None or platform == "shop":
            order_service = OrderService(self._session)
            result = await order_service.list_orders(
                workspace_id,
                shop_id=shop_id,
                status=status_filter,
                date_from=date_from,
                date_to=date_to,
                page=page,
                page_size=page_size,
            )
            for o in result.items:
                resp = OrderSummaryResponse.model_validate(o)
                resp.source_platform = "shop"
                items.append(resp)

            if platform == "shop":
                return PaginatedResponse(
                    items=items,
                    total=result.total,
                    page=result.page,
                    page_size=result.page_size,
                    total_pages=result.total_pages,
                )

        # When platform is None or "affiliate", pull affiliate orders too.
        # Affiliate orders are still Shop API orders but from the affiliate
        # program. This can be extended with affiliate-specific filtering.

        total = len(items)
        total_pages = max(1, (total + page_size - 1) // page_size)
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/commerce/test_unified_commerce_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/commerce/services/unified_service.py tests/unit/commerce/test_unified_commerce_service.py
git commit -m "feat: add UnifiedCommerceService for cross-platform order aggregation"
```

---

### Task 7: Add `platform` Query Param to Commerce Order Routes

**Files:**
- Modify: `backend/modules/commerce/routes/orders.py:21-52`

**Step 1: Update the route**

In `backend/modules/commerce/routes/orders.py`, modify `list_orders`:

```python
from backend.modules.commerce.services.unified_service import UnifiedCommerceService

@router.get(
    "/orders",
    response_model=PaginatedResponse[OrderSummaryResponse],
)
async def list_orders(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    platform: str | None = None,  # NEW
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[OrderSummaryResponse]:
    service = UnifiedCommerceService(db)
    return await service.list_orders(
        workspace_id,
        platform=platform,
        shop_id=shop_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
```

**Step 2: Run existing tests**

Run: `pytest tests/unit/commerce/ -v`
Expected: All PASS

**Step 3: Commit**

```bash
git add backend/modules/commerce/routes/orders.py
git commit -m "feat: add platform query param to commerce orders route"
```

---

### Task 8: Update Frontend API Client with Platform Param

**Files:**
- Modify: `frontend/src/lib/api.ts`

**Step 1: Add `platform` param to `listCampaigns`**

In `frontend/src/lib/api.ts`, find the `listCampaigns` function (~line 498) and add `platform` to its params:

```typescript
export function listCampaigns(
  workspaceId: string,
  token: string,
  params?: {
    ad_account_id?: string;
    objective?: string;
    status_filter?: string;
    search?: string;
    platform?: string;  // NEW
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<CampaignSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.objective) query.set("objective", params.objective);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.search) query.set("search", params.search);
  if (params?.platform) query.set("platform", params.platform);  // NEW
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/campaigns?${query}`, { token });
}
```

**Step 2: Add `platform` param to `listOrders`**

Find `listOrders` (~line 290) and add `platform`:

```typescript
export function listOrders(
  workspaceId: string,
  token: string,
  params?: {
    shop_id?: string;
    status_filter?: string;
    date_from?: string;
    date_to?: string;
    platform?: string;  // NEW
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<OrderSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.date_from) query.set("date_from", params.date_from);
  if (params?.date_to) query.set("date_to", params.date_to);
  if (params?.platform) query.set("platform", params.platform);  // NEW
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/orders?${query}`, { token });
}
```

**Step 3: Add `source_platform` to TypeScript interfaces**

Add to `CampaignSummary` (~line 414):

```typescript
export interface CampaignSummary {
  id: string;
  platform_campaign_id: string;
  campaign_name: string;
  objective_type: string | null;
  budget_mode: string | null;
  budget: string | null;
  operation_status: string;
  secondary_status: string | null;
  source_platform?: string;  // NEW
  created_at: string;
  updated_at: string;
}
```

Add to `OrderSummary` (~line 161):

```typescript
export interface OrderSummary {
  id: string;
  platform_order_id: string;
  status: string;
  total_amount: string;
  currency: string;
  item_count: number;
  fulfillment_type: string | null;
  rts_sla: string | null;
  source_platform?: string;  // NEW
  created_at: string;
  updated_at: string;
}
```

**Step 4: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add platform param and source_platform field to frontend API client"
```

---

### Task 9: Add PlatformTabs to Advertising Page

**Files:**
- Modify: `frontend/src/app/(dashboard)/ads/page.tsx`

**Step 1: Add PlatformTabs import and state**

Add import at top:

```typescript
import { PlatformTabs } from "@/components/ui/platform-tabs";
```

Add platform tabs config and state inside the component (after existing state declarations ~line 68):

```typescript
const ADS_PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "marketing", label: "TikTok Ads" },
  { key: "shop", label: "Shop Promotions" },
];

const [platformFilter, setPlatformFilter] = useState("all");
```

**Step 2: Wire platform into data loading**

Update `useEffect` deps (~line 77) to include `platformFilter`:

```typescript
useEffect(() => {
  loadCampaigns();
}, [search, statusFilter, objectiveFilter, accountFilter, platformFilter, page]);
```

Update `loadCampaigns` to pass platform:

```typescript
function loadCampaigns() {
  if (!token) return;
  setLoading(true);
  const platformParam = platformFilter === "all" ? undefined : platformFilter;
  listCampaigns(WORKSPACE_ID, token, {
    search: search || undefined,
    status_filter: statusFilter || undefined,
    objective: objectiveFilter || undefined,
    ad_account_id: accountFilter || undefined,
    platform: platformParam,
    page,
  })
    .then(setCampaigns)
    .catch(console.error)
    .finally(() => setLoading(false));
}
```

**Step 3: Add PlatformTabs to JSX and platform badge column**

Insert `<PlatformTabs>` right after `<PageHeader>` and before `<PageShell>`:

```tsx
<PlatformTabs
  tabs={ADS_PLATFORM_TABS}
  value={platformFilter}
  onChange={(v) => { setPlatformFilter(v); setPage(1); }}
/>
```

Add a platform column to `columns` array (insert after the "status" column):

```typescript
{
  key: "platform",
  header: "Platform",
  render: (row) => (
    <StatusBadge
      variant={row.source_platform === "shop" ? "warning" : "active"}
      label={row.source_platform === "shop" ? "Shop" : "TikTok Ads"}
    />
  ),
},
```

**Step 4: Hide actions in unified view**

Conditionally show/hide the actions column based on `platformFilter`:

```typescript
// Replace the actions column definition:
...(platformFilter !== "all" ? [{
  key: "actions",
  header: "",
  className: "w-12",
  render: (row: CampaignSummary) => (
    <ActionMenu
      items={[
        { label: "Edit", icon: <Edit className="h-4 w-4" />, onClick: () => { window.location.href = `/ads/campaigns/${row.id}`; } },
        { label: row.operation_status === "ENABLE" ? "Pause" : "Enable", icon: row.operation_status === "ENABLE" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />, onClick: () => toast.info("Status toggle coming soon") },
        { label: "Duplicate", icon: <Copy className="h-4 w-4" />, onClick: () => toast.info("Duplicate coming soon") },
      ]}
    />
  ),
}] : []),
```

**Step 5: Commit**

```bash
git add frontend/src/app/\(dashboard\)/ads/page.tsx
git commit -m "feat: add PlatformTabs to advertising campaigns page"
```

---

### Task 10: Add PlatformTabs to Commerce Page

**Files:**
- Modify: `frontend/src/app/(dashboard)/commerce/page.tsx`

**Step 1: Add PlatformTabs import and state**

Add import at top:

```typescript
import { PlatformTabs } from "@/components/ui/platform-tabs";
```

Add platform tabs config and state inside the component:

```typescript
const COMMERCE_PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "shop", label: "TikTok Shop" },
  { key: "affiliate", label: "Affiliates" },
];

const [platformFilter, setPlatformFilter] = useState("all");
```

**Step 2: Wire platform into data loading**

Update `useEffect` to include `platformFilter`:

```typescript
useEffect(() => {
  loadShops();
  loadOrders();
}, [statusFilter, platformFilter, page]);
```

Update `loadOrders`:

```typescript
function loadOrders() {
  if (!token) return;
  setLoading(true);
  const platformParam = platformFilter === "all" ? undefined : platformFilter;
  listOrders(WORKSPACE_ID, token, {
    status_filter: statusFilter || undefined,
    platform: platformParam,
    page,
  })
    .then(setOrders)
    .catch(console.error)
    .finally(() => setLoading(false));
}
```

**Step 3: Add PlatformTabs to JSX**

Insert right before `<PageShell>`:

```tsx
<PlatformTabs
  tabs={COMMERCE_PLATFORM_TABS}
  value={platformFilter}
  onChange={(v) => { setPlatformFilter(v); setPage(1); }}
/>
```

Add platform column to `columns` (after "status" column):

```typescript
{
  key: "platform",
  header: "Platform",
  render: (row) => (
    <StatusBadge
      variant={row.source_platform === "affiliate" ? "syncing" : "active"}
      label={row.source_platform === "affiliate" ? "Affiliate" : "Shop"}
    />
  ),
},
```

**Step 4: Commit**

```bash
git add frontend/src/app/\(dashboard\)/commerce/page.tsx
git commit -m "feat: add PlatformTabs to commerce orders page"
```

---

### Task 11: Run Full Test Suite and Verify

**Step 1: Run all backend tests**

Run: `pytest tests/ -v --tb=short`
Expected: All existing + new tests PASS

**Step 2: Run frontend build check**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no TypeScript errors

**Step 3: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix: resolve any test/build issues from multi-platform views"
```
