# Phase 2: Advertising Deep-Dive Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deepen the advertising module from 69% to ~95% Marketing API coverage by adding Business Center management, creative uploads, catalog deepening (product sets, feeds, insights), and Pangle.

**Architecture:** Extend existing advertising module patterns — `AdAccountService._get_gateway(ad_account)` for gateway access, `PaginatedResult` for list endpoints, mock gateway in tests via `patch.object(Service, "_get_gateway")`. New BC module uses the same Marketing API gateway but scoped to `bc_id` instead of `advertiser_id`.

**Tech Stack:** Python 3.12+ / FastAPI / SQLAlchemy async / pytest / TikTok Marketing API v1.3

---

## Current State

| Domain | Service | Methods | Routes | Coverage |
|--------|---------|---------|--------|----------|
| Campaigns | CampaignService | 7 (list, get, create, update, status, sync, upsert) | 6 | ~100% |
| Ad Groups | AdGroupService | 7 | 6 | ~100% |
| Ads | AdService | 7 | 6 | ~100% |
| Audiences | AudienceService | 10 (list, get, create custom/lookalike/rule, delete, sync, share, overlap, upload) | 8 | ~85% |
| Pixels | PixelService | 8 (list, get, create, code, sync, track, batch, upsert) | 6 | ~90% |
| Reports | ReportService | 6 (sync+cache, async create/check/download/cancel, GMV Max) | 6 | ~80% |
| Catalogs | CatalogService | 5 (list, get, create, add_products, sync) | 4 | ~40% |
| Creatives | CreativeService | 4 (portfolios list/create, smart_text, hashtags) | 4 | ~30% |
| Automation | AutomationService | 4 (list, create, update, delete rules) | 4 | 100% |
| Comments | CommentService | exists | exists | 100% |
| Search | SearchKeywordService | exists | exists | 100% |
| Symphony | SymphonyService | exists | exists | 100% |
| Split Tests | SplitTestService | exists | exists | 100% |
| Leads | LeadService | exists | exists | 100% |
| Identities | IdentityService | exists | exists | 100% |
| Change Log | ChangeLogService | exists | exists | 100% |
| Custom Conversions | CustomConversionService | exists | exists | 100% |
| **Business Center** | **NONE** | 0 | 0 | **0%** |
| **Pangle** | **NONE** | 0 | 0 | **0%** |

## Gap Analysis — What This Plan Adds

| Task | New Methods | New Routes | New Tests |
|------|------------|------------|-----------|
| 1. BC Core + Members | 7 | 6 | ~10 |
| 2. BC Partners + Assets | 8 | 7 | ~10 |
| 3. BC Finance | 7 | 6 | ~10 |
| 4. Creative Uploads | 6 | 5 | ~10 |
| 5. Catalog Product Sets | 6 | 5 | ~10 |
| 6. Catalog Feeds | 6 | 5 | ~10 |
| 7. Catalog Insights + Diagnostics | 7 | 5 | ~10 |
| 8. Pangle Management | 3 | 3 | ~8 |
| 9. Store + Showcase | 4 | 4 | ~8 |
| 10. Regression | 0 | 0 | verify all |
| **Total** | **~54** | **~46** | **~96** |

---

### Task 1: Business Center Core + Members

**Files:**
- Create: `backend/modules/advertising/services/business_center_service.py`
- Create: `backend/modules/advertising/routes/business_center.py`
- Modify: `backend/modules/advertising/routes/__init__.py` — add BC router
- Modify: `backend/modules/advertising/schemas.py` — add BC schemas
- Create: `tests/unit/test_business_center_core.py`

**Context:** Business Center is TikTok's centralized management hub for organizations (agencies, enterprises) — 0% coverage currently. Uses same Marketing API gateway but requests use `bc_id` param. The service needs a `_get_gateway(ad_account)` helper like other services.

**Step 1: Write failing tests**

```python
# tests/unit/test_business_center_core.py
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from backend.modules.advertising.services.business_center_service import BusinessCenterService

@pytest.fixture
def mock_gateway():
    gw = AsyncMock()
    return gw

@pytest.fixture
def service(db_session):
    return BusinessCenterService(db_session)

@pytest.mark.asyncio
async def test_list_business_centers(service, mock_gateway):
    mock_gateway.get.return_value = {"data": {"list": [{"bc_id": "bc1", "bc_name": "Agency BC"}]}}
    with patch.object(service, "_get_gateway", return_value=mock_gateway):
        result = await service.list_business_centers(ad_account=MagicMock())
    assert result["list"][0]["bc_id"] == "bc1"

@pytest.mark.asyncio
async def test_get_activity_log(service, mock_gateway):
    mock_gateway.get.return_value = {"data": {"list": [{"action": "CREATE"}]}}
    with patch.object(service, "_get_gateway", return_value=mock_gateway):
        result = await service.get_activity_log(ad_account=MagicMock(), bc_id="bc1")
    assert len(result["list"]) == 1

@pytest.mark.asyncio
async def test_list_members(service, mock_gateway):
    mock_gateway.get.return_value = {"data": {"list": [{"email": "user@test.com", "role": "ADMIN"}]}}
    with patch.object(service, "_get_gateway", return_value=mock_gateway):
        result = await service.list_members(ad_account=MagicMock(), bc_id="bc1")
    assert result["list"][0]["role"] == "ADMIN"

@pytest.mark.asyncio
async def test_invite_member(service, mock_gateway):
    mock_gateway.post.return_value = {"data": {"member_id": "m1"}}
    with patch.object(service, "_get_gateway", return_value=mock_gateway):
        result = await service.invite_member(ad_account=MagicMock(), bc_id="bc1", emails=["u@t.com"], role="OPERATOR")
    mock_gateway.post.assert_called_once()

@pytest.mark.asyncio
async def test_update_member(service, mock_gateway):
    mock_gateway.post.return_value = {"data": {}}
    with patch.object(service, "_get_gateway", return_value=mock_gateway):
        result = await service.update_member(ad_account=MagicMock(), bc_id="bc1", member_id="m1", role="ANALYST")
    mock_gateway.post.assert_called_once()

@pytest.mark.asyncio
async def test_delete_member(service, mock_gateway):
    mock_gateway.post.return_value = {"data": {}}
    with patch.object(service, "_get_gateway", return_value=mock_gateway):
        result = await service.delete_member(ad_account=MagicMock(), bc_id="bc1", member_id="m1")
    mock_gateway.post.assert_called_once()
```

**Step 2: Run tests — expect FAIL (module not found)**

```bash
pytest tests/unit/test_business_center_core.py -v
```

**Step 3: Implement BusinessCenterService**

Service methods:
- `list_business_centers(ad_account)` → `GET /bc/get/`
- `get_activity_log(ad_account, bc_id)` → `GET /bc/activity_log/get/`
- `list_members(ad_account, bc_id)` → `GET /bc/member/get/`
- `invite_member(ad_account, bc_id, emails, role)` → `POST /bc/member/invite/`
- `update_member(ad_account, bc_id, member_id, role)` → `POST /bc/member/update/`
- `delete_member(ad_account, bc_id, member_id)` → `POST /bc/member/delete/`

Routes (6): GET `/bc`, GET `/bc/{bc_id}/activity-log`, GET `/bc/{bc_id}/members`, POST `/bc/{bc_id}/members/invite`, PUT `/bc/{bc_id}/members/{member_id}`, DELETE `/bc/{bc_id}/members/{member_id}`

Schemas: `BCResponse`, `BCMemberResponse`, `InviteMemberRequest`, `UpdateMemberRequest`

**Step 4: Run tests — expect PASS**

```bash
pytest tests/unit/test_business_center_core.py -v
```

**Step 5: Commit**

```bash
git add backend/modules/advertising/services/business_center_service.py backend/modules/advertising/routes/business_center.py backend/modules/advertising/routes/__init__.py backend/modules/advertising/schemas.py tests/unit/test_business_center_core.py
git commit -m "feat(ads): add Business Center core + member management"
```

---

### Task 2: BC Partners + Asset Management

**Files:**
- Modify: `backend/modules/advertising/services/business_center_service.py`
- Modify: `backend/modules/advertising/routes/business_center.py`
- Modify: `backend/modules/advertising/schemas.py`
- Create: `tests/unit/test_bc_partners_assets.py`

**Context:** Extends BC service with partner management (add/remove external agencies) and asset management (assign/unassign ad accounts, pixels, audiences to members/partners).

**Step 1: Write failing tests**

Tests for:
- `list_partners(ad_account, bc_id)` → `GET /bc/partner/get/`
- `add_partner(ad_account, bc_id, partner_bc_id)` → `POST /bc/partner/add/`
- `delete_partner(ad_account, bc_id, partner_bc_id)` → `POST /bc/partner/delete/`
- `list_assets(ad_account, bc_id)` → `GET /bc/asset/get/`
- `assign_asset(ad_account, bc_id, asset_id, member_ids)` → `POST /bc/asset/assign/`
- `unassign_asset(ad_account, bc_id, asset_id, member_ids)` → `POST /bc/asset/unassign/`
- `create_ad_account_in_bc(ad_account, bc_id, name, timezone, currency)` → `POST /bc/asset/ad_account/create/`
- `get_partner_assets(ad_account, bc_id, partner_bc_id)` → `GET /bc/partner/asset/get/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement partner + asset methods in BusinessCenterService**

Routes (7): GET `/bc/{bc_id}/partners`, POST `/bc/{bc_id}/partners`, DELETE `/bc/{bc_id}/partners/{partner_bc_id}`, GET `/bc/{bc_id}/assets`, POST `/bc/{bc_id}/assets/assign`, POST `/bc/{bc_id}/assets/unassign`, POST `/bc/{bc_id}/ad-accounts`

Schemas: `BCPartnerResponse`, `AddPartnerRequest`, `BCAssetResponse`, `AssignAssetRequest`, `CreateBCAdAccountRequest`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add BC partner management + asset assignment"
```

---

### Task 3: BC Finance (Payments, Billing, Invoices)

**Files:**
- Modify: `backend/modules/advertising/services/business_center_service.py`
- Modify: `backend/modules/advertising/routes/business_center.py`
- Modify: `backend/modules/advertising/schemas.py`
- Create: `tests/unit/test_bc_finance.py`

**Context:** BC finance covers fund transfers between BC and ad accounts, balance queries, transaction records, billing groups, and invoices.

**Step 1: Write failing tests**

Tests for:
- `get_bc_balance(ad_account, bc_id)` → `GET /bc/payment/balance/get/`
- `process_payment(ad_account, bc_id, advertiser_id, transfer_type, amount)` → `POST /bc/payment/process/`
- `list_transactions(ad_account, bc_id)` → `GET /bc/payment/transaction/get/`
- `list_billing_groups(ad_account, bc_id)` → `GET /bc/billing_group/get/`
- `create_billing_group(ad_account, bc_id, name, advertiser_ids)` → `POST /bc/billing_group/create/`
- `list_invoices(ad_account, bc_id)` → `GET /bc/invoice/get/`
- `get_cost_records(ad_account, bc_id)` → `GET /bc/payment/cost/get/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement finance methods + routes (6)**

Routes: GET `/bc/{bc_id}/balance`, POST `/bc/{bc_id}/payments`, GET `/bc/{bc_id}/transactions`, GET `/bc/{bc_id}/billing-groups`, POST `/bc/{bc_id}/billing-groups`, GET `/bc/{bc_id}/invoices`

Schemas: `BCBalanceResponse`, `ProcessPaymentRequest`, `BCTransactionResponse`, `BillingGroupResponse`, `CreateBillingGroupRequest`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add BC finance — payments, billing groups, invoices"
```

---

### Task 4: Creative Upload & Management

**Files:**
- Modify: `backend/modules/advertising/services/creative_service.py`
- Modify: `backend/modules/advertising/routes/creatives.py`
- Modify: `backend/modules/advertising/schemas.py`
- Create: `tests/unit/test_creative_uploads.py`

**Context:** Currently CreativeService has 4 methods (portfolios, smart text, hashtags). Marketing API supports video upload, image upload, music library, and ad creative info. All use the same `_get_gateway(ad_account)` pattern.

**Step 1: Write failing tests**

Tests for:
- `upload_video(ad_account, video_url)` → `POST /file/video/ad/upload/` (upload by URL)
- `get_video_info(ad_account, video_ids)` → `GET /file/video/ad/info/`
- `upload_image(ad_account, image_url)` → `POST /file/image/ad/upload/` (upload by URL)
- `get_image_info(ad_account, image_ids)` → `GET /file/image/ad/info/`
- `search_music(ad_account, query)` → `GET /creative/music/search/`
- `get_ad_creative_info(ad_account, ad_ids)` → `GET /creative/ads/info/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement 6 new methods + 5 routes**

Routes: POST `/creatives/videos/upload`, GET `/creatives/videos/info`, POST `/creatives/images/upload`, GET `/creatives/images/info`, GET `/creatives/music/search`

Schemas: `UploadVideoRequest`, `UploadImageRequest`, `VideoInfoResponse`, `ImageInfoResponse`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add creative upload — video, image, music search"
```

---

### Task 5: Catalog Product Sets

**Files:**
- Modify: `backend/modules/advertising/services/catalog_service.py`
- Modify: `backend/modules/advertising/routes/catalogs.py`
- Modify: `backend/modules/advertising/schemas.py`
- Create: `tests/unit/test_catalog_product_sets.py`

**Context:** Product sets are subsets of catalog products defined by rules or manual selection, used for targeting specific products in ad groups. Currently CatalogService has no product set support.

**Step 1: Write failing tests**

Tests for:
- `list_product_sets(ad_account, catalog_id)` → `GET /catalog/product_set/get/`
- `get_product_set_products(ad_account, catalog_id, product_set_id)` → `GET /catalog/product_set/product/get/`
- `create_product_set_by_conditions(ad_account, catalog_id, name, conditions)` → `POST /catalog/product_set/condition/create/`
- `create_product_set_by_file(ad_account, catalog_id, name, file_url)` → `POST /catalog/product_set/file/create/`
- `update_product_set(ad_account, catalog_id, product_set_id, updates)` → `POST /catalog/product_set/update/`
- `delete_product_sets(ad_account, catalog_id, product_set_ids)` → `POST /catalog/product_set/delete/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement 6 methods + 5 routes**

Routes: GET `/catalogs/{catalog_id}/product-sets`, GET `/catalogs/{catalog_id}/product-sets/{set_id}/products`, POST `/catalogs/{catalog_id}/product-sets/by-condition`, POST `/catalogs/{catalog_id}/product-sets/by-file`, DELETE `/catalogs/{catalog_id}/product-sets`

Schemas: `ProductSetResponse`, `CreateProductSetConditionRequest`, `CreateProductSetFileRequest`, `DeleteProductSetsRequest`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add catalog product set CRUD"
```

---

### Task 6: Catalog Feeds

**Files:**
- Modify: `backend/modules/advertising/services/catalog_service.py`
- Modify: `backend/modules/advertising/routes/catalogs.py`
- Modify: `backend/modules/advertising/schemas.py`
- Create: `tests/unit/test_catalog_feeds.py`

**Context:** Feeds allow automated, scheduled product updates from external data sources (CSV/XML URLs). Currently no feed support exists.

**Step 1: Write failing tests**

Tests for:
- `list_feeds(ad_account, catalog_id)` → `GET /catalog/feed/get/`
- `create_feed(ad_account, catalog_id, name, url, schedule)` → `POST /catalog/feed/create/`
- `update_feed(ad_account, catalog_id, feed_id, updates)` → `POST /catalog/feed/update/`
- `delete_feed(ad_account, catalog_id, feed_id)` → `POST /catalog/feed/delete/`
- `get_feed_log(ad_account, catalog_id, feed_id)` → `GET /catalog/feed/log/`
- `update_feed_schedule(ad_account, catalog_id, feed_id, schedule)` → `POST /catalog/feed/schedule/update/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement 6 methods + 5 routes**

Routes: GET `/catalogs/{catalog_id}/feeds`, POST `/catalogs/{catalog_id}/feeds`, PUT `/catalogs/{catalog_id}/feeds/{feed_id}`, DELETE `/catalogs/{catalog_id}/feeds/{feed_id}`, GET `/catalogs/{catalog_id}/feeds/{feed_id}/log`

Schemas: `CatalogFeedResponse`, `CreateFeedRequest`, `UpdateFeedRequest`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add catalog feed management with scheduling"
```

---

### Task 7: Catalog Insights, Diagnostics, Event Sources

**Files:**
- Modify: `backend/modules/advertising/services/catalog_service.py`
- Modify: `backend/modules/advertising/routes/catalogs.py`
- Modify: `backend/modules/advertising/schemas.py`
- Create: `tests/unit/test_catalog_insights.py`

**Context:** Catalog insights surface trending products/categories. Diagnostics help troubleshoot product quality and event source match rates. Event sources link pixels/apps to catalogs for retargeting.

**Step 1: Write failing tests**

Tests for:
- `get_catalog_overview(ad_account, catalog_id)` → `GET /catalog/overview/get/`
- `get_trending_products(ad_account, catalog_id)` → `GET /catalog/insights/product/trending/`
- `get_trending_categories(ad_account, catalog_id)` → `GET /catalog/insights/category/trending/`
- `get_product_diagnostics(ad_account, catalog_id)` → `GET /catalog/diagnostics/product/get/`
- `get_event_source_diagnostics(ad_account, catalog_id)` → `GET /catalog/diagnostics/event_source/get/`
- `bind_event_source(ad_account, catalog_id, pixel_id)` → `POST /catalog/event_source/bind/`
- `unbind_event_source(ad_account, catalog_id, pixel_id)` → `POST /catalog/event_source/unbind/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement 7 methods + 5 routes**

Routes: GET `/catalogs/{catalog_id}/overview`, GET `/catalogs/{catalog_id}/insights/trending-products`, GET `/catalogs/{catalog_id}/diagnostics`, POST `/catalogs/{catalog_id}/event-sources/bind`, POST `/catalogs/{catalog_id}/event-sources/unbind`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add catalog insights, diagnostics, event source binding"
```

---

### Task 8: Pangle Management

**Files:**
- Create: `backend/modules/advertising/services/pangle_service.py`
- Create: `backend/modules/advertising/routes/pangle.py`
- Modify: `backend/modules/advertising/routes/__init__.py` — add pangle router
- Create: `tests/unit/test_pangle_service.py`

**Context:** Pangle is TikTok's ad network extending reach to third-party apps. 3 API endpoints for block list management and audience packages. Uses same `_get_gateway(ad_account)` pattern.

**Step 1: Write failing tests**

Tests for:
- `get_block_list(ad_account)` → `GET /pangle/block_list/get/`
- `update_block_list(ad_account, block_list, action)` → `POST /pangle/block_list/update/`
- `get_audience_packages(ad_account)` → `GET /pangle/audience_package/get/`

Plus tests for ADD and REMOVE actions on block list.

**Step 2: Run tests — expect FAIL**

**Step 3: Implement PangleService + routes**

Routes: GET `/pangle/block-list`, POST `/pangle/block-list`, GET `/pangle/audience-packages`

Schemas: `PangleBlockListResponse`, `UpdateBlockListRequest`, `PangleAudiencePackageResponse`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add Pangle block list + audience package management"
```

---

### Task 9: Store + Showcase Integration

**Files:**
- Create: `backend/modules/advertising/services/store_service.py`
- Create: `backend/modules/advertising/routes/store.py`
- Modify: `backend/modules/advertising/routes/__init__.py` — add store router
- Create: `tests/unit/test_store_service.py`

**Context:** TikTok Store integration allows accessing shop products from the Marketing API side (for catalog ads). Showcase integration provides creator-linked product access. Uses same gateway pattern.

**Step 1: Write failing tests**

Tests for:
- `list_stores(ad_account)` → `GET /store/get/`
- `get_store_products(ad_account, store_id)` → `GET /store/product/get/`
- `get_showcase_identities(ad_account)` → `GET /showcase/identity/get/`
- `get_showcase_products(ad_account, identity_id)` → `GET /showcase/product/get/`

**Step 2: Run tests — expect FAIL**

**Step 3: Implement StoreService + routes**

Routes: GET `/store`, GET `/store/{store_id}/products`, GET `/showcase/identities`, GET `/showcase/{identity_id}/products`

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git commit -m "feat(ads): add TikTok Store + Showcase product integration"
```

---

### Task 10: Regression + Full Test Suite Verification

**Files:**
- All test files in `tests/`

**Step 1: Run the full test suite**

```bash
pytest tests/ -v --tb=short 2>&1 | tail -50
```

Expected: All tests pass (previous 695 + ~96 new ≈ 791+)

**Step 2: Verify no import errors in new modules**

```bash
python -c "from backend.modules.advertising.routes import router; print('OK')"
```

**Step 3: Count total endpoints**

```bash
grep -r "@router\." backend/modules/advertising/routes/ | wc -l
```

Expected: ~140+ advertising endpoints

**Step 4: Commit if any fixes needed**

```bash
git commit -m "test: Phase 2 advertising deep-dive regression verification"
```

---

## Post-Phase 2 Coverage

| Domain | Before | After |
|--------|--------|-------|
| Business Center | 0% | ~80% (core, members, partners, assets, finance) |
| Creatives | 30% | ~75% (+ video/image upload, music, ad info) |
| Catalogs | 40% | ~90% (+ product sets, feeds, insights, diagnostics, event sources) |
| Pangle | 0% | 100% (block lists, audience packages) |
| Store/Showcase | 0% | 100% (store products, showcase) |
| **Overall** | **69%** | **~92%** |
