# Phase 1: Commerce Deep-Dive Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deepen the Commerce module from read-only sync to full CRUD + management, covering ~90 missing TikTok Shop API capabilities across Products, Orders, Fulfillment, Returns, Finance, Logistics, and Seller.

**Architecture:** Extend existing service/route/schema pattern. Each service method wraps a TikTok Shop API call via `ShopService.build_gateway_for_shop()` → `PlatformGateway`. All write operations call TikTok API first, then persist locally. Tests mock the gateway.

**Tech Stack:** Python 3.12 / FastAPI / SQLAlchemy async / pytest / TikTok Shop API v202309

---

### Task 1: Product Categories & Attributes

**Files:**
- Modify: `backend/modules/commerce/services/product_service.py`
- Modify: `backend/modules/commerce/routes/products.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_product_categories.py`

**Context:** TikTok Shop requires category selection + attribute filling before product creation. These are prerequisite APIs (Get Categories, Recommend Categories, Get Category Rules, Get Attributes). Currently missing entirely.

**Step 1: Write failing tests**

```python
# tests/unit/test_product_categories.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session


@pytest.fixture
def mock_gateway():
    gw = AsyncMock()
    return gw


class TestGetCategories:
    @pytest.mark.asyncio
    async def test_get_categories_returns_tree(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {
            "data": {
                "categories": [
                    {"id": "1", "parent_id": "0", "local_name": "Electronics", "is_leaf": False},
                    {"id": "2", "parent_id": "1", "local_name": "Phones", "is_leaf": True},
                ]
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_categories(shop_id=MagicMock())
            assert len(result) == 2
            assert result[0]["local_name"] == "Electronics"

    @pytest.mark.asyncio
    async def test_recommend_categories(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {
            "data": {"categories": [{"id": "100", "local_name": "Shoes"}]}
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.recommend_categories(
                shop_id=MagicMock(), product_title="Nike Air Max"
            )
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_attributes(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {
            "data": {
                "attributes": [
                    {"id": "a1", "name": "Color", "is_required": True},
                ]
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_attributes(
                shop_id=MagicMock(), category_id="100"
            )
            assert result[0]["name"] == "Color"

    @pytest.mark.asyncio
    async def test_get_category_rules(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {
            "data": {"category_rules": [{"property": "size_chart", "is_required": True}]}
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.get_category_rules(
                shop_id=MagicMock(), category_id="100"
            )
            assert len(result) >= 1
```

**Step 2: Run tests to verify they fail**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_product_categories.py -v`
Expected: FAIL — methods don't exist on ProductService

**Step 3: Implement — add `_get_gateway` helper + 4 category methods to ProductService**

Add to `product_service.py`:
```python
async def _get_gateway(self, shop_id: uuid.UUID) -> "PlatformGateway":
    shop_service = ShopService(self._session)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise ValueError(f"Shop {shop_id} not found")
    return await shop_service.build_gateway_for_shop(shop)

async def get_categories(self, shop_id: uuid.UUID) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get("/product/202309/categories")
    return resp.get("data", {}).get("categories", [])

async def recommend_categories(self, shop_id: uuid.UUID, product_title: str) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post(
        "/product/202309/categories/recommend",
        json_body={"product_title": product_title},
    )
    return resp.get("data", {}).get("categories", [])

async def get_category_rules(self, shop_id: uuid.UUID, category_id: str) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/product/202309/categories/{category_id}/rules")
    return resp.get("data", {}).get("category_rules", [])

async def get_attributes(self, shop_id: uuid.UUID, category_id: str) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/product/202309/categories/{category_id}/attributes")
    return resp.get("data", {}).get("attributes", [])
```

Add schemas to `schemas.py`:
```python
class CategoryResponse(BaseModel):
    id: str
    parent_id: str | None = None
    local_name: str
    is_leaf: bool = False

class AttributeResponse(BaseModel):
    id: str
    name: str
    is_required: bool = False
```

Add routes to `products.py`:
```python
@router.get("/products/categories")
async def get_categories(shop_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> list[dict]:
    service = ProductService(db)
    return await service.get_categories(shop_id)

@router.post("/products/categories/recommend")
async def recommend_categories(shop_id: uuid.UUID, product_title: str, current_user: CurrentUser, db: DBSession) -> list[dict]:
    service = ProductService(db)
    return await service.recommend_categories(shop_id, product_title)

@router.get("/products/categories/{category_id}/rules")
async def get_category_rules(category_id: str, shop_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> list[dict]:
    service = ProductService(db)
    return await service.get_category_rules(shop_id, category_id)

@router.get("/products/categories/{category_id}/attributes")
async def get_attributes(category_id: str, shop_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> list[dict]:
    service = ProductService(db)
    return await service.get_attributes(shop_id, category_id)
```

**Step 4: Run tests to verify they pass**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/unit/test_product_categories.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add tests/unit/test_product_categories.py backend/modules/commerce/services/product_service.py backend/modules/commerce/routes/products.py backend/modules/commerce/schemas.py
git commit -m "feat(commerce): add product categories & attributes APIs"
```

---

### Task 2: Product Create

**Files:**
- Modify: `backend/modules/commerce/services/product_service.py`
- Modify: `backend/modules/commerce/routes/products.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_product_create.py`

**Context:** Core product creation via TikTok Shop API POST `/product/202309/products`. Requires category_id, title, description, images, SKUs with price/inventory. The API returns the created product which we persist locally.

**Step 1: Write failing tests**

```python
# tests/unit/test_product_create.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestCreateProduct:
    @pytest.mark.asyncio
    async def test_create_product_calls_api_and_persists(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {
            "data": {
                "product_id": "prod_123",
                "skus": [{"id": "sku_1"}],
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.create_product(
                workspace_id=uuid.uuid4(),
                shop_id=uuid.uuid4(),
                title="Test Product",
                description="A product",
                category_id="cat_1",
                images=[{"url": "https://example.com/img.jpg"}],
                skus=[{"seller_sku": "SKU-001", "price": {"amount": "1999", "currency": "USD"}, "inventory": [{"quantity": 100}]}],
            )
            mock_gateway.post.assert_called_once()
            call_args = mock_gateway.post.call_args
            assert "/product/202309/products" in call_args[0][0]
            assert result["product_id"] == "prod_123"

    @pytest.mark.asyncio
    async def test_create_product_persists_locally(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {
            "data": {"product_id": "prod_456", "skus": []}
        }
        # Mock the upsert to track it was called
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            with patch.object(ProductService, "upsert_product_from_api") as mock_upsert:
                mock_upsert.return_value = MagicMock()
                service = ProductService(mock_session)
                await service.create_product(
                    workspace_id=uuid.uuid4(),
                    shop_id=uuid.uuid4(),
                    title="Test",
                    description="Desc",
                    category_id="cat_1",
                    images=[],
                    skus=[],
                )
```

**Step 2: Run tests — expect FAIL**

**Step 3: Implement `create_product` in ProductService**

```python
async def create_product(
    self,
    workspace_id: uuid.UUID,
    shop_id: uuid.UUID,
    *,
    title: str,
    description: str,
    category_id: str,
    images: list[dict],
    skus: list[dict],
    package_dimensions: dict | None = None,
) -> dict:
    """Create a product on TikTok Shop and persist locally."""
    gateway = await self._get_gateway(shop_id)
    body: dict = {
        "title": title,
        "description": description,
        "category_id": category_id,
        "main_images": [{"uri": img.get("url", img.get("uri", ""))} for img in images],
        "skus": skus,
    }
    if package_dimensions:
        body["package_dimensions"] = package_dimensions

    resp = await gateway.post("/product/202309/products", json_body=body)
    data = resp.get("data", {})

    # Fetch full product detail to persist
    product_id = data.get("product_id", "")
    if product_id:
        detail_resp = await gateway.get(f"/product/202309/products/{product_id}")
        product_data = detail_resp.get("data", {})
        if product_data:
            shop = await ShopService(self._session).get_shop(shop_id)
            if shop:
                await self.upsert_product_from_api(shop=shop, product_data=product_data)

    return data
```

Add schema:
```python
class CreateProductRequest(BaseModel):
    shop_id: str
    title: str
    description: str
    category_id: str
    images: list[dict] = []
    skus: list[dict] = []
    package_dimensions: dict | None = None
```

Add route:
```python
@router.post("/products", status_code=201)
async def create_product(body: CreateProductRequest, workspace_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> dict:
    service = ProductService(db)
    return await service.create_product(
        workspace_id, uuid.UUID(body.shop_id),
        title=body.title, description=body.description, category_id=body.category_id,
        images=body.images, skus=body.skus, package_dimensions=body.package_dimensions,
    )
```

**Step 4: Run tests — expect PASS**

**Step 5: Commit**

```bash
git add tests/unit/test_product_create.py backend/modules/commerce/services/product_service.py backend/modules/commerce/routes/products.py backend/modules/commerce/schemas.py
git commit -m "feat(commerce): add product creation via TikTok Shop API"
```

---

### Task 3: Product Edit & Partial Edit

**Files:**
- Modify: `backend/modules/commerce/services/product_service.py`
- Modify: `backend/modules/commerce/routes/products.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_product_edit.py`

**Context:** Two endpoints: PUT `/product/202309/products/{product_id}` (full edit) and PUT `/product/202312/products/{product_id}/partial_edit` (partial). Full edit replaces all fields, partial edit updates only provided fields.

**Step 1: Write failing tests**

```python
# tests/unit/test_product_edit.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestEditProduct:
    @pytest.mark.asyncio
    async def test_edit_product_calls_put(self, mock_session, mock_gateway):
        mock_gateway.put.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.edit_product(
                shop_id=uuid.uuid4(),
                platform_product_id="prod_1",
                title="Updated Title",
                description="Updated desc",
                category_id="cat_1",
                images=[],
                skus=[],
            )
            mock_gateway.put.assert_called_once()
            assert "/product/202309/products/prod_1" in mock_gateway.put.call_args[0][0]


class TestPartialEditProduct:
    @pytest.mark.asyncio
    async def test_partial_edit_product(self, mock_session, mock_gateway):
        mock_gateway.put.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.partial_edit_product(
                shop_id=uuid.uuid4(),
                platform_product_id="prod_1",
                title="New Title Only",
            )
            mock_gateway.put.assert_called_once()
            call_body = mock_gateway.put.call_args[1].get("json_body", {})
            assert call_body.get("title") == "New Title Only"
```

**Step 2: Run — FAIL**

**Step 3: Implement `edit_product` and `partial_edit_product`**

```python
async def edit_product(
    self, shop_id: uuid.UUID, platform_product_id: str, *,
    title: str, description: str, category_id: str,
    images: list[dict], skus: list[dict],
) -> dict:
    gateway = await self._get_gateway(shop_id)
    body = {
        "title": title, "description": description,
        "category_id": category_id,
        "main_images": [{"uri": img.get("url", img.get("uri", ""))} for img in images],
        "skus": skus,
    }
    resp = await gateway.put(f"/product/202309/products/{platform_product_id}", json_body=body)
    return resp.get("data", {})

async def partial_edit_product(
    self, shop_id: uuid.UUID, platform_product_id: str, **fields: Any,
) -> dict:
    gateway = await self._get_gateway(shop_id)
    body = {k: v for k, v in fields.items() if v is not None}
    resp = await gateway.put(
        f"/product/202312/products/{platform_product_id}/partial_edit",
        json_body=body,
    )
    return resp.get("data", {})
```

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add product full edit and partial edit"
```

---

### Task 4: Product Lifecycle (Delete, Activate, Deactivate, Recover)

**Files:**
- Modify: `backend/modules/commerce/services/product_service.py`
- Modify: `backend/modules/commerce/routes/products.py`
- Test: `tests/unit/test_product_lifecycle.py`

**Context:** Batch operations on products: POST `delete-products`, `activate-products`, `deactivate-products`, `recover-products`. All accept `product_ids` array.

**Step 1: Write failing tests**

```python
# tests/unit/test_product_lifecycle.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.product_service import ProductService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestProductLifecycle:
    @pytest.mark.asyncio
    async def test_delete_products(self, mock_session, mock_gateway):
        mock_gateway.delete.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.delete_products(shop_id=uuid.uuid4(), product_ids=["p1", "p2"])
            mock_gateway.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_products(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.activate_products(shop_id=uuid.uuid4(), product_ids=["p1"])
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_products(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.deactivate_products(shop_id=uuid.uuid4(), product_ids=["p1"])
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_recover_products(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.recover_products(shop_id=uuid.uuid4(), product_ids=["p1"])
            mock_gateway.post.assert_called_once()
```

**Step 2: Run — FAIL**

**Step 3: Implement 4 lifecycle methods + routes**

```python
async def delete_products(self, shop_id: uuid.UUID, product_ids: list[str]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.delete("/product/202309/products", json_body={"product_ids": product_ids})
    return resp.get("data", {})

async def activate_products(self, shop_id: uuid.UUID, product_ids: list[str]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/product/202309/products/activate", json_body={"product_ids": product_ids})
    return resp.get("data", {})

async def deactivate_products(self, shop_id: uuid.UUID, product_ids: list[str]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/product/202309/products/deactivate", json_body={"product_ids": product_ids})
    return resp.get("data", {})

async def recover_products(self, shop_id: uuid.UUID, product_ids: list[str]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/product/202309/products/recover", json_body={"product_ids": product_ids})
    return resp.get("data", {})
```

Routes:
```python
@router.post("/products/delete")
@router.post("/products/activate")
@router.post("/products/deactivate")
@router.post("/products/recover")
```

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add product lifecycle actions (delete/activate/deactivate/recover)"
```

---

### Task 5: Product Price & Inventory Update

**Files:**
- Modify: `backend/modules/commerce/services/product_service.py`
- Modify: `backend/modules/commerce/routes/products.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_product_price_inventory.py`

**Context:** POST `/product/202309/products/prices` (update prices for SKUs) and POST `/product/202309/products/inventory` (update inventory for SKUs). Both accept product_id + list of SKU updates.

**Step 1: Write failing tests**

```python
# tests/unit/test_product_price_inventory.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.product_service import ProductService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestUpdatePrice:
    @pytest.mark.asyncio
    async def test_update_price(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.update_price(
                shop_id=uuid.uuid4(),
                product_id="prod_1",
                skus=[{"id": "sku_1", "price": {"amount": "2999", "currency": "USD"}}],
            )
            mock_gateway.post.assert_called_once()
            assert "prices" in mock_gateway.post.call_args[0][0]


class TestUpdateInventory:
    @pytest.mark.asyncio
    async def test_update_inventory(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.update_inventory_api(
                shop_id=uuid.uuid4(),
                product_id="prod_1",
                skus=[{"id": "sku_1", "inventory": [{"quantity": 50}]}],
            )
            mock_gateway.post.assert_called_once()
            assert "inventory" in mock_gateway.post.call_args[0][0]
```

**Step 2: Run — FAIL**

**Step 3: Implement**

```python
async def update_price(self, shop_id: uuid.UUID, product_id: str, skus: list[dict]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post(
        "/product/202309/products/prices",
        json_body={"product_id": product_id, "skus": skus},
    )
    return resp.get("data", {})

async def update_inventory_api(self, shop_id: uuid.UUID, product_id: str, skus: list[dict]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post(
        "/product/202309/products/inventory",
        json_body={"product_id": product_id, "skus": skus},
    )
    return resp.get("data", {})
```

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add product price and inventory update APIs"
```

---

### Task 6: Product Image Upload

**Files:**
- Modify: `backend/modules/commerce/services/product_service.py`
- Modify: `backend/modules/commerce/routes/products.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_product_image_upload.py`

**Context:** POST `/product/202309/images/upload` (upload image) and POST `/product/202309/files/upload` (upload file/certification). These return URIs for use in product create/edit.

**Step 1: Write failing tests**

```python
# tests/unit/test_product_image_upload.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.product_service import ProductService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestImageUpload:
    @pytest.mark.asyncio
    async def test_upload_image_returns_uri(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {
            "data": {"uri": "tos-maliva-i-xxx/image.jpg", "url": "https://cdn.tiktok.com/image.jpg"}
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.upload_product_image(
                shop_id=uuid.uuid4(), image_url="https://example.com/img.jpg"
            )
            assert "uri" in result

    @pytest.mark.asyncio
    async def test_upload_file_returns_uri(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {
            "data": {"uri": "tos-maliva-i-xxx/cert.pdf", "url": "https://cdn.tiktok.com/cert.pdf"}
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.upload_product_file(
                shop_id=uuid.uuid4(), file_url="https://example.com/cert.pdf", file_name="cert.pdf"
            )
            assert "uri" in result
```

**Step 2: Run — FAIL**

**Step 3: Implement**

```python
async def upload_product_image(self, shop_id: uuid.UUID, image_url: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post(
        "/product/202309/images/upload",
        json_body={"img_url": image_url},
    )
    return resp.get("data", {})

async def upload_product_file(self, shop_id: uuid.UUID, file_url: str, file_name: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post(
        "/product/202309/files/upload",
        json_body={"file_url": file_url, "name": file_name},
    )
    return resp.get("data", {})
```

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add product image and file upload APIs"
```

---

### Task 7: Order Cancellation Management

**Files:**
- Modify: `backend/modules/commerce/services/order_service.py`
- Modify: `backend/modules/commerce/routes/orders.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_order_cancellation.py`

**Context:** TikTok API: cancel-order, approve-cancellation, reject-cancellation, search-cancellations, get-price-detail. Currently no cancellation support.

**Step 1: Write failing tests**

```python
# tests/unit/test_order_cancellation.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.modules.commerce.services.order_service import OrderService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestOrderCancellation:
    @pytest.mark.asyncio
    async def test_cancel_order(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.cancel_order(shop_id=uuid.uuid4(), order_id="ord_1", cancel_reason="Out of stock")
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_cancellation(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.approve_cancellation(shop_id=uuid.uuid4(), order_id="ord_1")
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_cancellation(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            await service.reject_cancellation(shop_id=uuid.uuid4(), order_id="ord_1", reject_reason="Already shipped")
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_cancellations(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"cancellations": [{"order_id": "ord_1"}]}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.search_cancellations(shop_id=uuid.uuid4())
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_price_detail(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"subtotal": "1999", "shipping": "499", "tax": "200"}}
        with patch.object(OrderService, "_get_gateway", return_value=mock_gateway):
            service = OrderService(mock_session)
            result = await service.get_price_detail(shop_id=uuid.uuid4(), order_id="ord_1")
            assert "subtotal" in result
```

**Step 2: Run — FAIL**

**Step 3: Implement `_get_gateway` + 5 methods on OrderService**

```python
async def _get_gateway(self, shop_id: uuid.UUID):
    shop_service = ShopService(self._session)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise ValueError(f"Shop {shop_id} not found")
    return await shop_service.build_gateway_for_shop(shop)

async def cancel_order(self, shop_id: uuid.UUID, order_id: str, cancel_reason: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/return_refund/202309/cancellations", json_body={"order_id": order_id, "cancel_reason": cancel_reason})
    return resp.get("data", {})

async def approve_cancellation(self, shop_id: uuid.UUID, order_id: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post(f"/return_refund/202309/cancellations/{order_id}/approve")
    return resp.get("data", {})

async def reject_cancellation(self, shop_id: uuid.UUID, order_id: str, reject_reason: str = "") -> dict:
    gateway = await self._get_gateway(shop_id)
    body: dict = {}
    if reject_reason:
        body["reject_reason"] = reject_reason
    resp = await gateway.post(f"/return_refund/202309/cancellations/{order_id}/reject", json_body=body if body else None)
    return resp.get("data", {})

async def search_cancellations(self, shop_id: uuid.UUID, **filters) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/return_refund/202309/cancellations/search", json_body=filters or {})
    return resp.get("data", {}).get("cancellations", [])

async def get_price_detail(self, shop_id: uuid.UUID, order_id: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/order/202407/orders/{order_id}/price_detail")
    return resp.get("data", {})
```

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add order cancellation management and price detail APIs"
```

---

### Task 8: Returns & Refunds Enrichment

**Files:**
- Modify: `backend/modules/commerce/services/return_service.py`
- Modify: `backend/modules/commerce/routes/returns.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_returns_enrichment.py`

**Context:** Add missing return APIs: create return, search returns, get return records, get reject reasons, calculate refund. Currently only list, approve, reject, and webhook upsert.

**Step 1: Write failing tests**

```python
# tests/unit/test_returns_enrichment.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.return_service import ReturnService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestReturnsEnrichment:
    @pytest.mark.asyncio
    async def test_create_return(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"return_id": "ret_1"}}
        with patch.object(ReturnService, "_get_gateway", return_value=mock_gateway):
            service = ReturnService(mock_session)
            result = await service.create_return(
                shop_id=uuid.uuid4(), order_id="ord_1",
                return_type="RETURN_AND_REFUND", reason="Defective",
            )
            assert result["return_id"] == "ret_1"

    @pytest.mark.asyncio
    async def test_search_returns(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"returns": [{"return_id": "ret_1"}]}}
        with patch.object(ReturnService, "_get_gateway", return_value=mock_gateway):
            service = ReturnService(mock_session)
            result = await service.search_returns(shop_id=uuid.uuid4())
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_return_records(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"records": [{"event": "created"}]}}
        with patch.object(ReturnService, "_get_gateway", return_value=mock_gateway):
            service = ReturnService(mock_session)
            result = await service.get_return_records(shop_id=uuid.uuid4(), return_id="ret_1")
            assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_reject_reasons(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"reasons": [{"id": "r1", "text": "Wrong item"}]}}
        with patch.object(ReturnService, "_get_gateway", return_value=mock_gateway):
            service = ReturnService(mock_session)
            result = await service.get_reject_reasons(shop_id=uuid.uuid4())
            assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_calculate_refund(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"refund_amount": "1999"}}
        with patch.object(ReturnService, "_get_gateway", return_value=mock_gateway):
            service = ReturnService(mock_session)
            result = await service.calculate_refund(
                shop_id=uuid.uuid4(), order_id="ord_1", items=[{"sku_id": "sku_1", "quantity": 1}]
            )
            assert result["refund_amount"] == "1999"
```

**Step 2: Run — FAIL**

**Step 3: Implement `_get_gateway` + 5 new methods on ReturnService**

```python
async def _get_gateway(self, shop_id: uuid.UUID):
    from backend.modules.commerce.services.shop_service import ShopService
    shop_service = ShopService(self._session)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise ValueError(f"Shop {shop_id} not found")
    return await shop_service.build_gateway_for_shop(shop)

async def create_return(self, shop_id: uuid.UUID, order_id: str, return_type: str, reason: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/return_refund/202309/returns", json_body={
        "order_id": order_id, "return_type": return_type, "reason": reason,
    })
    return resp.get("data", {})

async def search_returns(self, shop_id: uuid.UUID, **filters) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/return_refund/202309/returns/search", json_body=filters or {})
    return resp.get("data", {}).get("returns", [])

async def get_return_records(self, shop_id: uuid.UUID, return_id: str) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/return_refund/202309/returns/{return_id}/records")
    return resp.get("data", {}).get("records", [])

async def get_reject_reasons(self, shop_id: uuid.UUID) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get("/return_refund/202309/reject_reasons")
    return resp.get("data", {}).get("reasons", [])

async def calculate_refund(self, shop_id: uuid.UUID, order_id: str, items: list[dict]) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/return_refund/202309/refund/calculate", json_body={
        "order_id": order_id, "items": items,
    })
    return resp.get("data", {})
```

Add routes for each new method.

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add returns/refunds enrichment (create, search, records, reject reasons, calculate)"
```

---

### Task 9: Fulfillment Enhancement

**Files:**
- Modify: `backend/modules/commerce/services/fulfillment_service.py`
- Modify: `backend/modules/commerce/routes/fulfillment.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_fulfillment_enhancement.py`

**Context:** Add missing: split orders, batch ship, package search, shipping documents, update shipping info, update delivery status. Currently only: ship, mark_shipped, get_shipping_services, get_tracking, get_package_detail.

**Step 1: Write failing tests**

```python
# tests/unit/test_fulfillment_enhancement.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.fulfillment_service import FulfillmentService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestFulfillmentEnhancement:
    @pytest.mark.asyncio
    async def test_split_order(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"packages": [{"id": "pkg_1"}, {"id": "pkg_2"}]}}
        with patch.object(FulfillmentService, "_get_gateway", return_value=mock_gateway):
            service = FulfillmentService(mock_session)
            result = await service.split_order(shop_id=uuid.uuid4(), order_id="ord_1", groups=[["sku_1"], ["sku_2"]])
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_batch_ship_packages(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"results": [{"package_id": "pkg_1", "success": True}]}}
        with patch.object(FulfillmentService, "_get_gateway", return_value=mock_gateway):
            service = FulfillmentService(mock_session)
            result = await service.batch_ship_packages(shop_id=uuid.uuid4(), packages=[
                {"order_id": "ord_1", "shipping_provider_id": "sp_1", "tracking_number": "TRK001"}
            ])
            assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_search_packages(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {"packages": [{"id": "pkg_1"}]}}
        with patch.object(FulfillmentService, "_get_gateway", return_value=mock_gateway):
            service = FulfillmentService(mock_session)
            result = await service.search_packages(shop_id=uuid.uuid4())
            assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_shipping_document(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"doc_url": "https://cdn.tiktok.com/label.pdf"}}
        with patch.object(FulfillmentService, "_get_gateway", return_value=mock_gateway):
            service = FulfillmentService(mock_session)
            result = await service.get_shipping_document(shop_id=uuid.uuid4(), package_id="pkg_1", document_type="SHIPPING_LABEL")
            assert "doc_url" in result

    @pytest.mark.asyncio
    async def test_update_shipping_info(self, mock_session, mock_gateway):
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(FulfillmentService, "_get_gateway", return_value=mock_gateway):
            service = FulfillmentService(mock_session)
            await service.update_shipping_info(shop_id=uuid.uuid4(), order_id="ord_1", tracking_number="TRK002", shipping_provider_id="sp_1")
            mock_gateway.post.assert_called_once()
```

**Step 2: Run — FAIL**

**Step 3: Implement `_get_gateway` + 5 methods on FulfillmentService**

```python
async def _get_gateway(self, shop_id: uuid.UUID):
    from backend.modules.commerce.services.shop_service import ShopService
    shop_service = ShopService(self._session)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise ValueError(f"Shop {shop_id} not found")
    return await shop_service.build_gateway_for_shop(shop)

async def split_order(self, shop_id: uuid.UUID, order_id: str, groups: list[list[str]]) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/fulfillment/202309/orders/split", json_body={"order_id": order_id, "groups": groups})
    return resp.get("data", {}).get("packages", [])

async def batch_ship_packages(self, shop_id: uuid.UUID, packages: list[dict]) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/fulfillment/202309/packages/batch_ship", json_body={"packages": packages})
    return resp.get("data", {}).get("results", [])

async def search_packages(self, shop_id: uuid.UUID, **filters) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/fulfillment/202309/packages/search", json_body=filters or {})
    return resp.get("data", {}).get("packages", [])

async def get_shipping_document(self, shop_id: uuid.UUID, package_id: str, document_type: str = "SHIPPING_LABEL") -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/fulfillment/202309/packages/{package_id}/shipping_document", params={"document_type": document_type})
    return resp.get("data", {})

async def update_shipping_info(self, shop_id: uuid.UUID, order_id: str, tracking_number: str, shipping_provider_id: str) -> dict:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.post("/fulfillment/202309/packages/shipping_info/update", json_body={
        "order_id": order_id, "tracking_number": tracking_number, "shipping_provider_id": shipping_provider_id,
    })
    return resp.get("data", {})
```

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add fulfillment enhancement (split, batch ship, search, docs, update)"
```

---

### Task 10: Logistics Module

**Files:**
- Create: `backend/modules/commerce/services/logistics_service.py`
- Create: `backend/modules/commerce/routes/logistics.py`
- Modify: `backend/modules/commerce/routes/__init__.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_logistics_service.py`

**Context:** New service for Logistics API: get warehouses, get delivery options, get shipping providers, get shipping templates. No existing code — 5 API endpoints.

**Step 1: Write failing tests**

```python
# tests/unit/test_logistics_service.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.logistics_service import LogisticsService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestLogisticsService:
    @pytest.mark.asyncio
    async def test_get_warehouses(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"warehouses": [
            {"id": "wh_1", "name": "Main Warehouse", "address": {}}
        ]}}
        with patch.object(LogisticsService, "_get_gateway", return_value=mock_gateway):
            service = LogisticsService(mock_session)
            result = await service.get_warehouses(shop_id=uuid.uuid4())
            assert len(result) == 1
            assert result[0]["name"] == "Main Warehouse"

    @pytest.mark.asyncio
    async def test_get_delivery_options(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"delivery_options": [
            {"id": "do_1", "name": "Standard", "shipping_type": "PLATFORM"}
        ]}}
        with patch.object(LogisticsService, "_get_gateway", return_value=mock_gateway):
            service = LogisticsService(mock_session)
            result = await service.get_delivery_options(shop_id=uuid.uuid4(), warehouse_id="wh_1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_shipping_providers(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"shipping_providers": [
            {"id": "sp_1", "name": "USPS Ground"}
        ]}}
        with patch.object(LogisticsService, "_get_gateway", return_value=mock_gateway):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_providers(shop_id=uuid.uuid4())
            assert len(result) == 1
```

**Step 2: Run — FAIL (module doesn't exist)**

**Step 3: Create `logistics_service.py`**

```python
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)

class LogisticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, shop_id: uuid.UUID):
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def get_warehouses(self, shop_id: uuid.UUID) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/logistics/202309/warehouses")
        return resp.get("data", {}).get("warehouses", [])

    async def get_delivery_options(self, shop_id: uuid.UUID, warehouse_id: str) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(f"/logistics/202309/warehouses/{warehouse_id}/delivery_options")
        return resp.get("data", {}).get("delivery_options", [])

    async def get_shipping_providers(self, shop_id: uuid.UUID) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/logistics/202309/shipping_providers")
        return resp.get("data", {}).get("shipping_providers", [])

    async def get_shipping_templates(self, shop_id: uuid.UUID) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/logistics/202510/shipping_templates")
        return resp.get("data", {}).get("shipping_templates", [])
```

Create `routes/logistics.py` + register in `__init__.py`.

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add logistics module (warehouses, delivery options, shipping providers)"
```

---

### Task 11: Finance Enrichment

**Files:**
- Modify: `backend/modules/commerce/services/finance_service.py`
- Modify: `backend/modules/commerce/routes/finance.py`
- Modify: `backend/modules/commerce/schemas.py`
- Test: `tests/unit/test_finance_enrichment.py`

**Context:** Add missing: get withdrawals, get transactions by order, get transactions by statement, get unsettled transactions. Currently: list settlements/transactions/payments + sync.

**Step 1: Write failing tests**

```python
# tests/unit/test_finance_enrichment.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.finance_service import FinanceService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestFinanceEnrichment:
    @pytest.mark.asyncio
    async def test_get_withdrawals(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"withdrawals": [{"id": "wd_1", "amount": "5000"}]}}
        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_withdrawals(shop_id=uuid.uuid4())
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_transactions_by_order(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"transactions": [{"type": "ORDER_PAYMENT"}]}}
        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_transactions_by_order(shop_id=uuid.uuid4(), order_id="ord_1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_transactions_by_statement(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"transactions": [{"type": "COMMISSION"}]}}
        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_transactions_by_statement(shop_id=uuid.uuid4(), statement_id="stm_1")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_unsettled_transactions(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"transactions": [{"type": "PENDING_SETTLEMENT"}]}}
        with patch.object(FinanceService, "_get_gateway", return_value=mock_gateway):
            service = FinanceService(mock_session)
            result = await service.get_unsettled_transactions(shop_id=uuid.uuid4())
            assert len(result) == 1
```

**Step 2: Run — FAIL**

**Step 3: Implement `_get_gateway` + 4 methods on FinanceService**

```python
async def _get_gateway(self, shop_id: uuid.UUID):
    shop_service = ShopService(self._session)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise ValueError(f"Shop {shop_id} not found")
    return await shop_service.build_gateway_for_shop(shop)

async def get_withdrawals(self, shop_id: uuid.UUID) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get("/finance/202309/withdrawals")
    return resp.get("data", {}).get("withdrawals", [])

async def get_transactions_by_order(self, shop_id: uuid.UUID, order_id: str) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/finance/202501/orders/{order_id}/transactions")
    return resp.get("data", {}).get("transactions", [])

async def get_transactions_by_statement(self, shop_id: uuid.UUID, statement_id: str) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get(f"/finance/202501/statements/{statement_id}/transactions")
    return resp.get("data", {}).get("transactions", [])

async def get_unsettled_transactions(self, shop_id: uuid.UUID) -> list[dict]:
    gateway = await self._get_gateway(shop_id)
    resp = await gateway.get("/finance/202507/transactions/unsettled")
    return resp.get("data", {}).get("transactions", [])
```

Add routes + schemas for each.

**Step 4: Run — PASS**

**Step 5: Commit**

```bash
git commit -m "feat(commerce): add finance enrichment (withdrawals, order/statement txns, unsettled)"
```

---

### Task 12: Seller Module + Regression Tests

**Files:**
- Create: `backend/modules/commerce/services/seller_service.py`
- Create: `backend/modules/commerce/routes/seller.py`
- Modify: `backend/modules/commerce/routes/__init__.py`
- Test: `tests/unit/test_seller_service.py`

**Context:** New service for Seller API: get active shops, get seller permissions. Simple 2-endpoint module. Then run full regression to verify nothing broke.

**Step 1: Write failing tests**

```python
# tests/unit/test_seller_service.py
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from backend.modules.commerce.services.seller_service import SellerService

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_gateway():
    return AsyncMock()


class TestSellerService:
    @pytest.mark.asyncio
    async def test_get_active_shops(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"shops": [
            {"id": "shop_1", "name": "My Shop", "region": "US", "status": "ACTIVE"}
        ]}}
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_active_shops(shop_id=uuid.uuid4())
            assert len(result) == 1
            assert result[0]["region"] == "US"

    @pytest.mark.asyncio
    async def test_get_seller_permissions(self, mock_session, mock_gateway):
        mock_gateway.get.return_value = {"data": {"permissions": [
            {"feature": "GLOBAL_PRODUCT", "enabled": True}
        ]}}
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_seller_permissions(shop_id=uuid.uuid4())
            assert len(result) == 1
```

**Step 2: Run — FAIL**

**Step 3: Create `seller_service.py`**

```python
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)

class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, shop_id: uuid.UUID):
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def get_active_shops(self, shop_id: uuid.UUID) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/seller/202309/shops")
        return resp.get("data", {}).get("shops", [])

    async def get_seller_permissions(self, shop_id: uuid.UUID) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/seller/202309/permissions")
        return resp.get("data", {}).get("permissions", [])
```

Create `routes/seller.py` + register in `__init__.py`.

**Step 4: Run seller tests — PASS**

**Step 5: Run full regression**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/ -v --tb=short`
Expected: All 578+ existing tests PASS + ~45 new tests PASS = 620+ total

**Step 6: Commit**

```bash
git commit -m "feat(commerce): add seller module + verify full regression (Phase 1 complete)"
```
