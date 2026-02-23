# Multi-Platform Views Design

**Date:** 2026-02-23
**Scope:** Advertising + Commerce modules
**Approach:** Platform Context + Query Filter (Approach 1)

## Goal

Add per-platform and unified views to Advertising and Commerce tabs. Users can toggle between seeing all TikTok sub-platforms merged (read-only) or drilling into a specific platform with full actions.

## Platform Mapping

| User-facing Tab | Backend `Platform` | API Client | Module |
|---|---|---|---|
| TikTok Ads | `MARKETING` | TikTokMarketingClient | Advertising |
| Shop Promotions | `SHOP` | TikTokShopClient | Advertising |
| TikTok Shop | `SHOP` | TikTokShopClient | Commerce |
| Affiliates | `SHOP` (affiliate subset) | TikTokShopClient | Commerce |

**Per-module tabs:**
- **Advertising:** All | TikTok Ads | Shop Promotions
- **Commerce:** All | TikTok Shop | Affiliates

## Backend Changes

### 1. Response Schema: `source_platform` Field

Every list endpoint response item includes `source_platform: str` to identify origin.

```python
class CampaignOut(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    # ... existing fields
    source_platform: str  # "marketing" | "shop"
```

### 2. Query Parameter: `?platform=`

Existing list routes accept optional `platform` query param:

```
GET /api/advertising/campaigns                    → all platforms (unified)
GET /api/advertising/campaigns?platform=marketing → Marketing API only
GET /api/advertising/campaigns?platform=shop      → Shop promotions only
```

### 3. Unified Service Layer

New thin aggregation services that call existing platform-specific services:

```python
class UnifiedAdvertisingService:
    """Aggregates data from Marketing + Shop services."""

    async def list_campaigns(
        self,
        workspace_id: UUID,
        platform: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[CampaignOut]:
        if platform == "marketing" or platform is None:
            marketing_items = await self._marketing_service.list_campaigns(...)
        if platform == "shop" or platform is None:
            shop_items = await self._shop_service.list_promotions(...)
        return merge_and_paginate(marketing_items, shop_items)
```

Similarly for `UnifiedCommerceService`.

## Frontend Changes

### 1. `PlatformTabs` Component (New)

Reusable secondary tab bar between page header and content.

```typescript
interface PlatformTabsProps {
  tabs: { key: string; label: string }[];
  value: string;       // current selection
  onChange: (key: string) => void;
}
```

Rendered below the main navigation tabs, above MetricBar.

### 2. URL-Driven State

Platform selection in `?platform=` search param (defaults to `all`). Shareable URLs.

### 3. Unified View ("All" Tab)

- DataTable adds "Platform" column with `StatusBadge`
- ActionMenu hidden (read-only)
- Clicking a row navigates to per-platform detail view
- MetricBar shows aggregated metrics

### 4. Per-Platform View

- Existing pages work exactly as today
- ActionMenu fully enabled
- MetricBar shows platform-specific metrics

## File Changes

| Layer | File | Change |
|---|---|---|
| **Frontend** | `components/ui/platform-tabs.tsx` | New reusable component |
| **Frontend** | `app/(dashboard)/ads/page.tsx` + sub-pages | Add PlatformTabs + platform filter |
| **Frontend** | `app/(dashboard)/commerce/page.tsx` + sub-pages | Add PlatformTabs + platform filter |
| **Frontend** | `lib/api.ts` | Add `platform` param to fetch functions |
| **Backend** | `modules/advertising/routes/*.py` | Add `platform` query param |
| **Backend** | `modules/commerce/routes/*.py` | Add `platform` query param |
| **Backend** | `modules/advertising/services/unified_service.py` | New aggregation service |
| **Backend** | `modules/commerce/services/unified_service.py` | New aggregation service |
| **Backend** | `modules/advertising/schemas/*.py` | Add `source_platform` field |
| **Backend** | `modules/commerce/schemas/*.py` | Add `source_platform` field |

## Data Flow

```
User selects platform tab
  → URL updates: ?platform=shop
  → useEffect triggers re-fetch
  → GET /api/advertising/campaigns?platform=shop
  → UnifiedAdvertisingService filters by Platform.SHOP
  → Response items include source_platform
  → DataTable renders with platform badge
```

## Constraints

- Unified view is **read-only** (no action-taking)
- Per-platform view has **full actions** (existing behavior)
- Start with Advertising + Commerce; other modules can adopt PlatformTabs later
- No new database tables required — uses existing `ConnectedAccount.platform` filtering
