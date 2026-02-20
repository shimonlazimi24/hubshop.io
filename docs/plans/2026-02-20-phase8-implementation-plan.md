# Phase 8: Automation & Engagement Platform — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add 4 new capability areas to Frodo — Search Ads, Symphony AI Creative Tools, Business Messaging & Organic Content, and Advanced Campaign Tools (Split Tests, Automated Rules expansion, Lead Gen, Identity Management). This expands the Marketing API surface from ~50 to ~130 advertising endpoints and adds 2 new modules (Messaging, Organic).

**Architecture:** All new services follow the existing gateway proxy pattern — services receive an `AdAccount` or `ConnectedAccount`, build a `PlatformGateway` via the account service, and proxy requests to TikTok Marketing API v1.3. New modules (messaging, organic) follow the same services + routes + models pattern. No new platform clients needed — all features use the existing Marketing API client.

**Tech Stack:** Python 3.12+ / FastAPI / SQLAlchemy async / Celery / Next.js 15 (unchanged from Phase 7)

**Design Doc:** N/A (scope derived from knowledge base gap analysis)

---

## Sub-Phase A: Search Ads Module

### Task 1: Create SearchKeywordService

**Files:**
- Create: `backend/modules/advertising/services/search_keyword_service.py`
- Test: `tests/unit/advertising/test_search_keyword_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/advertising/test_search_keyword_service.py
"""Tests for SearchKeywordService — keyword research, negative keywords, campaign health."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.search_keyword_service import (
    SearchKeywordService,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_account_service(
    sample_ad_account: SimpleNamespace, mock_gateway: AsyncMock
):
    with patch(
        "backend.modules.advertising.services.search_keyword_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestRecommendKeywords:
    @pytest.mark.asyncio
    async def test_recommend_keywords(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"keywords": [{"keyword": "sneakers", "bid": 1.5}]}
        }
        service = SearchKeywordService(mock_session)
        result = await service.recommend_keywords(
            sample_ad_account.workspace_id, sample_ad_account, keyword="shoes"
        )
        assert len(result["keywords"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestDiscoverKeywords:
    @pytest.mark.asyncio
    async def test_discover_keywords(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"keywords": [{"keyword": "running shoes", "volume": 5000}]}
        }
        service = SearchKeywordService(mock_session)
        result = await service.discover_keywords(
            sample_ad_account.workspace_id, sample_ad_account, keyword="shoes"
        )
        assert result["keywords"][0]["keyword"] == "running shoes"


class TestNegativeKeywords:
    @pytest.mark.asyncio
    async def test_list_negative_keywords(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"negative_keywords": [{"keyword_id": "nk1", "keyword": "cheap"}]}
        }
        service = SearchKeywordService(mock_session)
        result = await service.list_negative_keywords(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_group_id="ag1",
        )
        assert len(result["negative_keywords"]) == 1

    @pytest.mark.asyncio
    async def test_create_negative_keyword(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"keyword_id": "nk_new"}}
        service = SearchKeywordService(mock_session)
        result = await service.create_negative_keyword(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_group_id="ag1",
            keyword="cheap",
            match_type="EXACT",
        )
        assert result["keyword_id"] == "nk_new"

    @pytest.mark.asyncio
    async def test_delete_negative_keyword(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        service = SearchKeywordService(mock_session)
        result = await service.delete_negative_keyword(
            sample_ad_account.workspace_id,
            sample_ad_account,
            keyword_ids=["nk1"],
        )
        assert result == {}


class TestCampaignHealth:
    @pytest.mark.asyncio
    async def test_get_campaign_health(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"health_score": 85, "diagnoses": []}
        }
        service = SearchKeywordService(mock_session)
        result = await service.get_campaign_health(
            sample_ad_account.workspace_id,
            sample_ad_account,
            campaign_id="c1",
        )
        assert result["health_score"] == 85
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/amitkolton/Projects/Tiktok\ Frodo && .venv/bin/pytest tests/unit/advertising/test_search_keyword_service.py -v`
Expected: FAIL — module not found

**Step 3: Write minimal implementation**

```python
# backend/modules/advertising/services/search_keyword_service.py
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class SearchKeywordService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def recommend_keywords(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get recommended search keywords from TikTok."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/tool/keyword/recommend/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "keyword": keyword,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def discover_keywords(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Discover new keywords."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/tool/keyword/discover/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "keyword": keyword,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def list_negative_keywords(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_group_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List negative keywords for an ad group."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/negative_keywords/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_group_id": ad_group_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_negative_keyword(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_group_id: str,
        keyword: str,
        match_type: str = "EXACT",
    ) -> dict:
        """Create a negative keyword."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/negative_keywords/create/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "ad_group_id": ad_group_id,
                "keyword": keyword,
                "match_type": match_type,
            },
        )
        return resp.get("data", {})

    async def update_negative_keyword(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword_id: str,
        updates: dict,
    ) -> dict:
        """Update a negative keyword."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/negative_keywords/update/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "keyword_id": keyword_id,
                **updates,
            },
        )
        return resp.get("data", {})

    async def delete_negative_keyword(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword_ids: list[str],
    ) -> dict:
        """Delete negative keywords."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/negative_keywords/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "keyword_ids": keyword_ids,
            },
        )
        return resp.get("data", {})

    async def get_campaign_health(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        campaign_id: str,
    ) -> dict:
        """Get Search Ads campaign health diagnostics."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/tool/search_ads/health/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "campaign_id": campaign_id,
            },
        )
        return resp.get("data", {})
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/amitkolton/Projects/Tiktok\ Frodo && .venv/bin/pytest tests/unit/advertising/test_search_keyword_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/advertising/services/search_keyword_service.py tests/unit/advertising/test_search_keyword_service.py
git commit -m "feat: add SearchKeywordService for keyword research and negative keywords"
```

---

### Task 2: Create Search Ads routes

**Files:**
- Create: `backend/modules/advertising/routes/search.py`
- Modify: `backend/modules/advertising/routes/__init__.py`
- Test: `tests/unit/advertising/test_search_routes.py`

**Step 1: Write the route file**

```python
# backend/modules/advertising/routes/search.py
import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.search_keyword_service import (
    SearchKeywordService,
)

router = APIRouter()


class CreateNegativeKeywordRequest(BaseModel):
    ad_account_id: str
    ad_group_id: str
    keyword: str
    match_type: str = "EXACT"


class DeleteNegativeKeywordsRequest(BaseModel):
    ad_account_id: str
    keyword_ids: list[str]


@router.get("/search/keywords/recommend")
async def recommend_keywords(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    keyword: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = SearchKeywordService(db)
    return await service.recommend_keywords(
        workspace_id, ad_account, keyword=keyword, page=page, page_size=page_size
    )


@router.get("/search/keywords/discover")
async def discover_keywords(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    keyword: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = SearchKeywordService(db)
    return await service.discover_keywords(
        workspace_id, ad_account, keyword=keyword, page=page, page_size=page_size
    )


@router.get("/search/negative-keywords")
async def list_negative_keywords(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_group_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = SearchKeywordService(db)
    return await service.list_negative_keywords(
        workspace_id, ad_account, ad_group_id=ad_group_id, page=page, page_size=page_size
    )


@router.post("/search/negative-keywords")
async def create_negative_keyword(
    workspace_id: uuid.UUID,
    body: CreateNegativeKeywordRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(body.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = SearchKeywordService(db)
    return await service.create_negative_keyword(
        workspace_id,
        ad_account,
        ad_group_id=body.ad_group_id,
        keyword=body.keyword,
        match_type=body.match_type,
    )


@router.delete("/search/negative-keywords")
async def delete_negative_keywords(
    workspace_id: uuid.UUID,
    body: DeleteNegativeKeywordsRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(body.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = SearchKeywordService(db)
    return await service.delete_negative_keyword(
        workspace_id, ad_account, keyword_ids=body.keyword_ids
    )


@router.get("/search/health/{campaign_id}")
async def get_campaign_health(
    workspace_id: uuid.UUID,
    campaign_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )
    service = SearchKeywordService(db)
    return await service.get_campaign_health(
        workspace_id, ad_account, campaign_id=campaign_id
    )
```

**Step 2: Register the router**

In `backend/modules/advertising/routes/__init__.py`, add:
```python
from backend.modules.advertising.routes.search import router as search_router
# ... (after existing imports)
router.include_router(search_router)
```

**Step 3: Commit**

```bash
git add backend/modules/advertising/routes/search.py backend/modules/advertising/routes/__init__.py
git commit -m "feat: add Search Ads routes — keywords, negative keywords, health"
```

---

## Sub-Phase B: Symphony AI Creative Tools

### Task 3: Create SymphonyService

**Files:**
- Create: `backend/modules/advertising/services/symphony_service.py`
- Test: `tests/unit/advertising/test_symphony_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/advertising/test_symphony_service.py
"""Tests for SymphonyService — Smart Creative, Smart Text, CTA, Smart Fix, Fatigue."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.symphony_service import SymphonyService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_account_service(
    sample_ad_account: SimpleNamespace, mock_gateway: AsyncMock
):
    with patch(
        "backend.modules.advertising.services.symphony_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestSmartCreative:
    @pytest.mark.asyncio
    async def test_get_smart_creative_materials(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"materials": [{"id": "m1", "type": "video"}]}
        }
        service = SymphonyService(mock_session)
        result = await service.get_smart_creative_materials(
            sample_ad_account.workspace_id, sample_ad_account, ad_id="a1"
        )
        assert len(result["materials"]) == 1

    @pytest.mark.asyncio
    async def test_create_smart_creative_ad(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"ad_id": "a_new"}}
        service = SymphonyService(mock_session)
        result = await service.create_smart_creative_ad(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_config={"ad_group_id": "ag1", "materials": []},
        )
        assert result["ad_id"] == "a_new"


class TestSmartText:
    @pytest.mark.asyncio
    async def test_recommend_smart_text(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"texts": ["Shop now!", "Limited offer!"]}
        }
        service = SymphonyService(mock_session)
        result = await service.recommend_smart_text(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_text="Buy shoes",
        )
        assert len(result["texts"]) == 2


class TestCtaRecommend:
    @pytest.mark.asyncio
    async def test_recommend_cta(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"ctas": [{"text": "Shop Now", "id": "cta1"}]}
        }
        service = SymphonyService(mock_session)
        result = await service.recommend_cta(
            sample_ad_account.workspace_id,
            sample_ad_account,
            objective="CONVERSIONS",
        )
        assert result["ctas"][0]["text"] == "Shop Now"


class TestSmartFix:
    @pytest.mark.asyncio
    async def test_create_smart_fix_task(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"task_id": "fix_1"}}
        service = SymphonyService(mock_session)
        result = await service.create_smart_fix(
            sample_ad_account.workspace_id,
            sample_ad_account,
            creative_id="cr1",
        )
        assert result["task_id"] == "fix_1"

    @pytest.mark.asyncio
    async def test_get_smart_fix_result(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"task_id": "fix_1", "status": "COMPLETED", "issues": []}
        }
        service = SymphonyService(mock_session)
        result = await service.get_smart_fix_result(
            sample_ad_account.workspace_id,
            sample_ad_account,
            task_id="fix_1",
        )
        assert result["status"] == "COMPLETED"


class TestFatigueDetection:
    @pytest.mark.asyncio
    async def test_detect_fatigue(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"fatigued_ads": [{"ad_id": "a1", "fatigue_level": "HIGH"}]}
        }
        service = SymphonyService(mock_session)
        result = await service.detect_fatigue(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_ids=["a1", "a2"],
        )
        assert len(result["fatigued_ads"]) == 1
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/amitkolton/Projects/Tiktok\ Frodo && .venv/bin/pytest tests/unit/advertising/test_symphony_service.py -v`
Expected: FAIL — module not found

**Step 3: Write minimal implementation**

```python
# backend/modules/advertising/services/symphony_service.py
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class SymphonyService:
    """Proxy for TikTok Symphony AI Creative tools via Marketing API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def get_smart_creative_materials(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_id: str,
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/smart_creative/material/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_id": ad_id,
            },
        )
        return resp.get("data", {})

    async def create_smart_creative_ad(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_config: dict,
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/smart_creative/ad/create/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                **ad_config,
            },
        )
        return resp.get("data", {})

    async def update_smart_creative_materials(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_id: str,
        materials: list[dict],
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/smart_creative/material/update/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "ad_id": ad_id,
                "materials": materials,
            },
        )
        return resp.get("data", {})

    async def recommend_smart_text(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_text: str,
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/smart_text/recommend/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_text": ad_text,
            },
        )
        return resp.get("data", {})

    async def recommend_cta(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        objective: str,
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/cta/recommend/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "objective": objective,
            },
        )
        return resp.get("data", {})

    async def create_smart_fix(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        creative_id: str,
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/creative/smart_fix/create/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "creative_id": creative_id,
            },
        )
        return resp.get("data", {})

    async def get_smart_fix_result(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        task_id: str,
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/smart_fix/result/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        return resp.get("data", {})

    async def detect_fatigue(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_ids: list[str],
    ) -> dict:
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/fatigue/detect/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_ids": ",".join(ad_ids),
            },
        )
        return resp.get("data", {})
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/amitkolton/Projects/Tiktok\ Frodo && .venv/bin/pytest tests/unit/advertising/test_symphony_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/modules/advertising/services/symphony_service.py tests/unit/advertising/test_symphony_service.py
git commit -m "feat: add SymphonyService for AI creative tools — Smart Creative, Text, CTA, Fix, Fatigue"
```

---

### Task 4: Create Symphony routes

**Files:**
- Create: `backend/modules/advertising/routes/symphony.py`
- Modify: `backend/modules/advertising/routes/__init__.py`

**Step 1: Write the route file**

```python
# backend/modules/advertising/routes/symphony.py
import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.symphony_service import SymphonyService

router = APIRouter()


class SmartCreativeAdRequest(BaseModel):
    ad_account_id: str
    ad_config: dict


class SmartFixRequest(BaseModel):
    ad_account_id: str
    creative_id: str


@router.get("/symphony/smart-creative/materials")
async def get_smart_creative_materials(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.get_smart_creative_materials(workspace_id, ad_account, ad_id=ad_id)


@router.post("/symphony/smart-creative/ads")
async def create_smart_creative_ad(
    workspace_id: uuid.UUID,
    body: SmartCreativeAdRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(body.ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.create_smart_creative_ad(workspace_id, ad_account, ad_config=body.ad_config)


@router.get("/symphony/smart-text/recommend")
async def recommend_smart_text(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_text: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.recommend_smart_text(workspace_id, ad_account, ad_text=ad_text)


@router.get("/symphony/cta/recommend")
async def recommend_cta(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    objective: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.recommend_cta(workspace_id, ad_account, objective=objective)


@router.post("/symphony/smart-fix")
async def create_smart_fix(
    workspace_id: uuid.UUID,
    body: SmartFixRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(body.ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.create_smart_fix(workspace_id, ad_account, creative_id=body.creative_id)


@router.get("/symphony/smart-fix/{task_id}")
async def get_smart_fix_result(
    workspace_id: uuid.UUID,
    task_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.get_smart_fix_result(workspace_id, ad_account, task_id=task_id)


@router.get("/symphony/fatigue/detect")
async def detect_fatigue(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_ids: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found")
    service = SymphonyService(db)
    return await service.detect_fatigue(
        workspace_id, ad_account, ad_ids=ad_ids.split(",")
    )
```

**Step 2: Register the router**

In `backend/modules/advertising/routes/__init__.py`, add:
```python
from backend.modules.advertising.routes.symphony import router as symphony_router
router.include_router(symphony_router)
```

**Step 3: Commit**

```bash
git add backend/modules/advertising/routes/symphony.py backend/modules/advertising/routes/__init__.py
git commit -m "feat: add Symphony AI creative routes — 8 endpoints"
```

---

## Sub-Phase C: Business Messaging Module

### Task 5: Create DB models for messaging

**Files:**
- Create: `backend/db/models/messaging.py`
- Modify: `backend/db/models/__init__.py`

**Step 1: Write the models**

```python
# backend/db/models/messaging.py
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class AutoMessageType(str, enum.Enum):
    WELCOME = "WELCOME"
    SUGGESTED_QUESTION = "SUGGESTED_QUESTION"
    CHAT_PROMPT = "CHAT_PROMPT"


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

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
    tiktok_conversation_id: Mapped[str] = mapped_column(String(255), unique=True)
    participant_user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    participant_display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus), default=ConversationStatus.ACTIVE
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_conversations_workspace_status", "workspace_id", "status"),
    )


class Message(Base, UUIDMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tiktok_message_id: Mapped[str] = mapped_column(String(255), unique=True)
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection))
    content: Mapped[str] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AutoMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "auto_messages"

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
    tiktok_auto_message_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    message_type: Mapped[AutoMessageType] = mapped_column(Enum(AutoMessageType))
    content: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
```

**Step 2: Add imports to `__init__.py`**

Append to `backend/db/models/__init__.py`:
```python
from backend.db.models.messaging import (
    AutoMessage,
    AutoMessageType,
    Conversation,
    ConversationStatus,
    Message,
    MessageDirection,
)
```

And add to `__all__`: `"AutoMessage"`, `"AutoMessageType"`, `"Conversation"`, `"ConversationStatus"`, `"Message"`, `"MessageDirection"`

**Step 3: Commit**

```bash
git add backend/db/models/messaging.py backend/db/models/__init__.py
git commit -m "feat: add messaging DB models — Conversation, Message, AutoMessage"
```

---

### Task 6: Create MessagingService

**Files:**
- Create: `backend/modules/messaging/__init__.py`
- Create: `backend/modules/messaging/services/__init__.py`
- Create: `backend/modules/messaging/services/messaging_service.py`
- Test: `tests/unit/messaging/__init__.py`
- Test: `tests/unit/messaging/test_messaging_service.py`

**Step 1: Write the failing test**

```python
# tests/unit/messaging/test_messaging_service.py
"""Tests for MessagingService — conversations, messages, auto-messages."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.messaging.services.messaging_service import MessagingService


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_gateway(mock_gateway: AsyncMock):
    with patch(
        "backend.modules.messaging.services.messaging_service.PlatformGateway",
        return_value=mock_gateway,
    ):
        yield mock_gateway


class TestListConversations:
    @pytest.mark.asyncio
    async def test_list_conversations(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"conversations": [{"id": "c1"}]}
        }
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.list_conversations()
        assert len(result["conversations"]) == 1


class TestSendMessage:
    @pytest.mark.asyncio
    async def test_send_message(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.post.return_value = {"data": {"message_id": "msg_1"}}
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.send_message(
            conversation_id="c1", content="Hello!"
        )
        assert result["message_id"] == "msg_1"


class TestListMessages:
    @pytest.mark.asyncio
    async def test_list_messages(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"messages": [{"id": "m1", "text": "Hi"}]}
        }
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.list_messages(conversation_id="c1")
        assert len(result["messages"]) == 1


class TestAutoMessages:
    @pytest.mark.asyncio
    async def test_create_auto_message(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.post.return_value = {"data": {"auto_message_id": "am1"}}
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.create_auto_message(
            message_type="WELCOME", content="Welcome to our shop!"
        )
        assert result["auto_message_id"] == "am1"

    @pytest.mark.asyncio
    async def test_list_auto_messages(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"auto_messages": [{"id": "am1"}]}
        }
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.list_auto_messages()
        assert len(result["auto_messages"]) == 1

    @pytest.mark.asyncio
    async def test_delete_auto_message(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.delete_auto_message(auto_message_id="am1")
        assert result == {}


class TestCommentToMessage:
    @pytest.mark.asyncio
    async def test_toggle_comment_to_message(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, patched_gateway
    ) -> None:
        mock_gateway.post.return_value = {"data": {"enabled": True}}
        service = MessagingService(mock_session, connected_account_id=uuid.uuid4())
        result = await service.toggle_comment_to_message(enabled=True)
        assert result["enabled"] is True
```

**Step 2: Write the implementation**

The service will proxy to the Business Messaging API via PlatformGateway, following the pattern of other services but using the Marketing API base URL with `/business_messaging/` paths.

**Step 3: Commit**

```bash
git add backend/modules/messaging/ tests/unit/messaging/
git commit -m "feat: add MessagingService — conversations, messages, auto-messages, comment-to-message"
```

---

### Task 7: Create Messaging routes

**Files:**
- Create: `backend/modules/messaging/routes/__init__.py`
- Create: `backend/modules/messaging/routes/conversations.py`
- Create: `backend/modules/messaging/routes/auto_messages.py`
- Modify: `backend/main.py`

**Step 1: Write routes**

Conversations: list, get messages, send message (5 endpoints)
Auto-messages: create, list, update, toggle, delete (5 endpoints)

**Step 2: Register in main.py**

```python
from backend.modules.messaging.routes import router as messaging_router
app.include_router(messaging_router, prefix=api_prefix)
```

**Step 3: Commit**

```bash
git add backend/modules/messaging/routes/ backend/main.py
git commit -m "feat: add messaging routes — 10 endpoints for conversations and auto-messages"
```

---

## Sub-Phase D: Organic Content Module

### Task 8: Create DB models for organic content

**Files:**
- Create: `backend/db/models/organic.py`
- Modify: `backend/db/models/__init__.py`

Models: `BrandMention`, `MentionKeyword`, `OrganicComment`

**Step 1: Write models**

```python
# backend/db/models/organic.py — BrandMention, MentionKeyword, OrganicComment
```

**Step 2: Commit**

```bash
git add backend/db/models/organic.py backend/db/models/__init__.py
git commit -m "feat: add organic content DB models — BrandMention, MentionKeyword, OrganicComment"
```

---

### Task 9: Create OrganicAccountService

**Files:**
- Create: `backend/modules/organic/__init__.py`
- Create: `backend/modules/organic/services/__init__.py`
- Create: `backend/modules/organic/services/account_service.py`
- Test: `tests/unit/organic/__init__.py`
- Test: `tests/unit/organic/test_account_service.py`

Service methods:
- `get_profile()` — GET /accounts/profile/
- `get_posts()` — GET /accounts/posts/
- `get_benchmarks()` — GET /accounts/benchmarks/
- `publish_video()` — POST /accounts/posts/video/publish/
- `publish_photo()` — POST /accounts/posts/photo/publish/
- `get_publish_status()` — GET /accounts/posts/status/
- `recommend_hashtags()` — GET /accounts/posts/hashtags/recommend/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/organic/ tests/unit/organic/
git commit -m "feat: add OrganicAccountService — profile, posts, publishing, hashtag recommendations"
```

---

### Task 10: Create MentionsService

**Files:**
- Create: `backend/modules/organic/services/mentions_service.py`
- Test: `tests/unit/organic/test_mentions_service.py`

Service methods:
- `get_top_mentions()` — GET /mentions/posts/top/
- `get_mention_detail()` — GET /mentions/posts/detail/
- `get_frequent_keywords()` — GET /mentions/keywords/frequent/
- `get_frequent_hashtags()` — GET /mentions/hashtags/frequent/
- `get_top_comment_mentions()` — GET /mentions/comments/top/
- `reply_to_mention()` — POST /mentions/comments/reply/
- `enable_brand_hashtag()` — POST /mentions/brand_hashtag/enable/
- `list_enabled_hashtags()` — GET /mentions/brand_hashtag/enabled/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/organic/services/mentions_service.py tests/unit/organic/test_mentions_service.py
git commit -m "feat: add MentionsService — brand mentions, keywords, hashtags, replies"
```

---

### Task 11: Create Organic routes and register

**Files:**
- Create: `backend/modules/organic/routes/__init__.py`
- Create: `backend/modules/organic/routes/accounts.py`
- Create: `backend/modules/organic/routes/mentions.py`
- Modify: `backend/main.py`

Accounts: 7 endpoints
Mentions: 8 endpoints

**Step 1: Write routes, register in main.py**

```python
from backend.modules.organic.routes import router as organic_router
app.include_router(organic_router, prefix=api_prefix)
```

**Step 2: Commit**

```bash
git add backend/modules/organic/ backend/main.py
git commit -m "feat: add organic content routes — accounts (7) + mentions (8) = 15 endpoints"
```

---

## Sub-Phase E: Advanced Campaign Tools

### Task 12: Create SplitTestService

**Files:**
- Create: `backend/modules/advertising/services/split_test_service.py`
- Test: `tests/unit/advertising/test_split_test_service.py`

Service methods:
- `create_split_test()` — POST /split_test/create/
- `update_test_time()` — POST /split_test/time/update/
- `end_split_test()` — POST /split_test/end/
- `get_results()` — GET /split_test/results/
- `apply_winner()` — POST /split_test/winner/apply/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/advertising/services/split_test_service.py tests/unit/advertising/test_split_test_service.py
git commit -m "feat: add SplitTestService — A/B testing create, results, apply winner"
```

---

### Task 13: Create LeadService

**Files:**
- Create: `backend/modules/advertising/services/lead_service.py`
- Test: `tests/unit/advertising/test_lead_service.py`

Service methods:
- `create_test_lead()` — POST /leads/test/create/
- `get_test_lead()` — GET /leads/test/get/
- `create_download_task()` — POST /leads/download/create/
- `download_leads()` — GET /leads/download/
- `get_form_libraries()` — GET /leads/form/libraries/
- `get_form_fields()` — GET /leads/form/fields/
- `get_leads()` — GET /leads/get/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/advertising/services/lead_service.py tests/unit/advertising/test_lead_service.py
git commit -m "feat: add LeadService — lead generation forms, download, test leads"
```

---

### Task 14: Create IdentityService

**Files:**
- Create: `backend/modules/advertising/services/identity_service.py`
- Test: `tests/unit/advertising/test_identity_service.py`

Service methods:
- `create_identity()` — POST /identity/create/
- `delete_identity()` — DELETE /identity/delete/
- `list_identities()` — GET /identity/list/
- `get_identity_detail()` — GET /identity/detail/
- `get_identity_posts()` — GET /identity/posts/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/advertising/services/identity_service.py tests/unit/advertising/test_identity_service.py
git commit -m "feat: add IdentityService — create, delete, list, detail, posts"
```

---

### Task 15: Create ChangeLogService

**Files:**
- Create: `backend/modules/advertising/services/change_log_service.py`
- Test: `tests/unit/advertising/test_change_log_service.py`

Service methods:
- `create_download_task()` — POST /change_log/download/create/
- `get_task_status()` — GET /change_log/download/status/
- `download_file()` — GET /change_log/download/file/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/advertising/services/change_log_service.py tests/unit/advertising/test_change_log_service.py
git commit -m "feat: add ChangeLogService — download, status, file retrieval"
```

---

### Task 16: Create CustomConversionService

**Files:**
- Create: `backend/modules/advertising/services/custom_conversion_service.py`
- Test: `tests/unit/advertising/test_custom_conversion_service.py`

Service methods:
- `list_conversions()` — GET /custom_conversion/list/
- `get_conversion_detail()` — GET /custom_conversion/detail/
- `create_conversion()` — POST /custom_conversion/create/
- `update_conversion()` — POST /custom_conversion/update/
- `delete_conversion()` — DELETE /custom_conversion/delete/

**Step 1-5: TDD cycle, commit**

```bash
git add backend/modules/advertising/services/custom_conversion_service.py tests/unit/advertising/test_custom_conversion_service.py
git commit -m "feat: add CustomConversionService — CRUD for custom conversions"
```

---

### Task 17: Create routes for advanced campaign tools

**Files:**
- Create: `backend/modules/advertising/routes/split_tests.py`
- Create: `backend/modules/advertising/routes/leads.py`
- Create: `backend/modules/advertising/routes/identities.py`
- Create: `backend/modules/advertising/routes/change_log.py`
- Create: `backend/modules/advertising/routes/custom_conversions.py`
- Modify: `backend/modules/advertising/routes/__init__.py`

Split tests: 5 endpoints
Leads: 7 endpoints
Identities: 5 endpoints
Change log: 3 endpoints
Custom conversions: 5 endpoints

Total: 25 new endpoints

**Step 1: Write all route files, register in __init__.py**

**Step 2: Commit**

```bash
git add backend/modules/advertising/routes/ tests/unit/advertising/
git commit -m "feat: add advanced campaign tool routes — split tests, leads, identities, change log, custom conversions"
```

---

## Sub-Phase F: Celery Workers

### Task 18: Create messaging sync worker

**Files:**
- Create: `backend/workers/messaging_sync.py`
- Modify: `backend/workers/celery_app.py`
- Test: `tests/unit/workers/test_messaging_sync.py`

Workers:
- `sync_conversations` — Every 30min, sync new conversations and messages
- `sync_mentions` — Every 2h, sync brand mentions for all workspaces

**Step 1-5: TDD cycle, commit**

```bash
git add backend/workers/messaging_sync.py backend/workers/celery_app.py tests/unit/workers/test_messaging_sync.py
git commit -m "feat: add messaging and mentions sync Celery workers with beat schedule"
```

---

## Sub-Phase G: Frontend Pages

### Task 19: Search Ads frontend page

**Files:**
- Create: `frontend/src/app/(dashboard)/ads/search/page.tsx`

Page shows: keyword research tool, negative keyword management, campaign health cards.

---

### Task 20: Symphony AI frontend page

**Files:**
- Create: `frontend/src/app/(dashboard)/ads/symphony/page.tsx`

Page shows: Smart Creative generator, Smart Text recommendations, CTA optimizer, Fatigue detector, Smart Fix launcher.

---

### Task 21: Messaging frontend pages

**Files:**
- Create: `frontend/src/app/(dashboard)/messaging/page.tsx`
- Create: `frontend/src/app/(dashboard)/messaging/[conversationId]/page.tsx`
- Create: `frontend/src/app/(dashboard)/messaging/auto-messages/page.tsx`
- Create: `frontend/src/app/(dashboard)/messaging/layout.tsx`

---

### Task 22: Organic Content frontend pages

**Files:**
- Create: `frontend/src/app/(dashboard)/organic/page.tsx`
- Create: `frontend/src/app/(dashboard)/organic/mentions/page.tsx`
- Create: `frontend/src/app/(dashboard)/organic/publish/page.tsx`
- Create: `frontend/src/app/(dashboard)/organic/layout.tsx`

---

### Task 23: Advanced campaign tools frontend pages

**Files:**
- Create: `frontend/src/app/(dashboard)/ads/split-tests/page.tsx`
- Create: `frontend/src/app/(dashboard)/ads/leads/page.tsx`
- Create: `frontend/src/app/(dashboard)/ads/identities/page.tsx`

---

### Task 24: Update sidebar navigation

**Files:**
- Modify: `frontend/src/config/navigation.ts`

Add:
```typescript
{ href: "/messaging", label: "Messaging", icon: MessageSquare, group: "Modules" },
{ href: "/organic", label: "Organic", icon: Sprout, group: "Modules" },
```

**Step 1: Commit all frontend pages**

```bash
git add frontend/
git commit -m "feat: add Phase 8 frontend pages — search ads, symphony, messaging, organic, advanced tools"
```

---

## Sub-Phase H: Integration & Verification

### Task 25: Run full test suite

Run: `cd /Users/amitkolton/Projects/Tiktok\ Frodo && .venv/bin/pytest tests/ -v --tb=short`
Expected: ALL PASS (463 existing + ~100 new = ~560+ total)

If failures: fix them before proceeding.

---

### Task 26: Final commit and summary

```bash
git add -A
git commit -m "feat: complete Phase 8 — Automation & Engagement Platform

- Search Ads: keyword research, negative keywords, campaign health (6 endpoints)
- Symphony AI: Smart Creative, Text, CTA, Fix, Fatigue Detection (8 endpoints)
- Business Messaging: conversations, messages, auto-messages (10 endpoints)
- Organic Content: accounts, posts, mentions, publishing (15 endpoints)
- Advanced Tools: split tests, leads, identities, change log, custom conversions (25 endpoints)
- 2 new modules (messaging, organic), 3 new DB model files
- 2 Celery workers (conversations sync, mentions sync)
- 14 new frontend pages
- ~560+ tests passing"
```
