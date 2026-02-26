# Connect Pipeline Overhaul — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the connect flow from developer-oriented OAuth into a polished app-installation experience with real-time sync progress, scope validation, and a sync health dashboard.

**Architecture:** New `SyncJob` model tracks each sync run per platform per workspace. Workers publish progress events to Redis pub/sub during sync. A new WebSocket endpoint (`/ws/connect/{workspace_id}`) streams these events to the frontend. Three new frontend pages: redesigned `/connect`, post-connect `/connect/sync`, and health dashboard `/connect/status`.

**Tech Stack:** Python 3.12+ / FastAPI / SQLAlchemy async / Celery / Redis pub/sub / WebSocket / Next.js 15 / TypeScript

---

## Context for Implementer

**Existing files you'll interact with:**
- `backend/db/models/platform.py` — `ConnectedAccount`, `TokenVault`, `Platform` enum, `AccountStatus` enum
- `backend/db/models/base.py` — `Base`, `UUIDMixin`, `TimestampMixin`
- `backend/modules/connect/routes.py` — 7 existing endpoints (3 authorize + 3 callback + 1 listing)
- `backend/modules/commerce/routes/ws.py` — Reference WebSocket pattern (Redis pub/sub + JWT auth)
- `backend/workers/data_sync.py` — Shop order/product sync workers
- `backend/workers/celery_app.py` — Celery beat schedule (17 periodic tasks)
- `frontend/src/lib/api.ts` — API client with `apiFetch`, `getAuthorizeUrl`, `listConnectedAccounts`
- `frontend/src/hooks/useCommerceWebSocket.ts` — Reference WebSocket hook pattern
- `frontend/src/app/(dashboard)/connect/page.tsx` — Current connect page (hardcoded workspace ID)

**Hardcoded workspace ID problem:** Frontend pages use `"00000000-0000-0000-0000-000000000000"` as workspace ID. The connect page and commerce page both do this. We'll fix it in the connect page by reading from the user's JWT payload (the `/auth/me` endpoint returns `workspace_id`).

**Scope constants to define:**
- Shop: Implicit scopes (controlled at TikTok Partner Center, not in URL)
- Developer: Already defined in `routes.py` line 20-29 as `DEVELOPER_SCOPES`
- Marketing: Implicit scopes (controlled at TikTok Ads Manager portal)

---

### Task 1: SyncJob Database Model

**Files:**
- Modify: `backend/db/models/platform.py`
- Test: `tests/unit/connect/test_sync_job_model.py`

**Step 1: Write the failing test**

Create `tests/unit/connect/__init__.py` (empty) and `tests/unit/connect/test_sync_job_model.py`:

```python
"""Tests for SyncJob model structure."""

import uuid
from datetime import UTC, datetime

import pytest

from backend.db.models.platform import SyncJob, SyncJobStatus


@pytest.mark.unit
class TestSyncJobModel:
    def test_sync_job_has_required_fields(self) -> None:
        job = SyncJob(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            platform="shop",
            sync_type="orders",
            status=SyncJobStatus.RUNNING,
        )
        assert job.workspace_id is not None
        assert job.platform == "shop"
        assert job.sync_type == "orders"
        assert job.status == SyncJobStatus.RUNNING
        assert job.items_synced == 0
        assert job.items_total is None
        assert job.error_message is None

    def test_sync_job_status_values(self) -> None:
        assert SyncJobStatus.PENDING.value == "pending"
        assert SyncJobStatus.RUNNING.value == "running"
        assert SyncJobStatus.COMPLETED.value == "completed"
        assert SyncJobStatus.FAILED.value == "failed"

    def test_sync_job_with_progress(self) -> None:
        job = SyncJob(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            platform="shop",
            sync_type="products",
            status=SyncJobStatus.RUNNING,
            items_synced=50,
            items_total=200,
        )
        assert job.items_synced == 50
        assert job.items_total == 200

    def test_sync_job_with_error(self) -> None:
        job = SyncJob(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            platform="marketing",
            sync_type="campaigns",
            status=SyncJobStatus.FAILED,
            error_message="API rate limited",
        )
        assert job.status == SyncJobStatus.FAILED
        assert job.error_message == "API rate limited"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/connect/test_sync_job_model.py -v`
Expected: FAIL with "cannot import name 'SyncJob'"

**Step 3: Write minimal implementation**

Add to `backend/db/models/platform.py` after `AccountStatus` enum:

```python
class SyncJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

Add after `PlatformAppCredential` class:

```python
class SyncJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sync_jobs"

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
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    sync_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of sync: orders, products, campaigns, videos, etc.",
    )
    status: Mapped[SyncJobStatus] = mapped_column(
        Enum(SyncJobStatus, name="sync_job_status_enum"),
        nullable=False,
        default=SyncJobStatus.PENDING,
    )
    items_synced: Mapped[int] = mapped_column(default=0)
    items_total: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

Also add `DateTime` to the imports from `sqlalchemy` (it's already imported in `base.py` but needed here).

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/connect/test_sync_job_model.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add backend/db/models/platform.py tests/unit/connect/
git commit -m "feat(connect): add SyncJob model for tracking sync runs"
```

---

### Task 2: SyncStatusService

**Files:**
- Create: `backend/modules/connect/services/__init__.py`
- Create: `backend/modules/connect/services/sync_status_service.py`
- Test: `tests/unit/connect/test_sync_status_service.py`

**Step 1: Write the failing test**

Create `tests/unit/connect/test_sync_status_service.py`:

```python
"""Tests for SyncStatusService — create, update progress, list jobs."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.platform import SyncJobStatus
from backend.modules.connect.services.sync_status_service import SyncStatusService


class TestCreateSyncJob:
    @pytest.mark.asyncio
    async def test_creates_job(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        workspace_id = uuid.uuid4()
        account_id = uuid.uuid4()

        service = SyncStatusService(session)
        job = await service.create_sync_job(
            workspace_id=workspace_id,
            connected_account_id=account_id,
            platform="shop",
            sync_type="orders",
        )

        assert session.add.called
        added = session.add.call_args[0][0]
        assert added.workspace_id == workspace_id
        assert added.platform == "shop"
        assert added.sync_type == "orders"
        assert added.status == SyncJobStatus.PENDING


class TestUpdateProgress:
    @pytest.mark.asyncio
    async def test_updates_progress(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            status=SyncJobStatus.RUNNING,
            items_synced=0,
            items_total=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        updated = await service.update_progress(job.id, items_synced=50, items_total=200)

        assert updated is not None
        assert updated.items_synced == 50
        assert updated.items_total == 200


class TestCompleteJob:
    @pytest.mark.asyncio
    async def test_marks_completed(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            status=SyncJobStatus.RUNNING,
            items_synced=200,
            items_total=200,
            completed_at=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        updated = await service.complete_job(job.id)

        assert updated.status == SyncJobStatus.COMPLETED
        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_marks_failed(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            status=SyncJobStatus.RUNNING,
            items_synced=50,
            items_total=200,
            completed_at=None,
            error_message=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        updated = await service.fail_job(job.id, "API rate limited")

        assert updated.status == SyncJobStatus.FAILED
        assert updated.error_message == "API rate limited"
        assert updated.completed_at is not None


class TestListJobs:
    @pytest.mark.asyncio
    async def test_list_recent_jobs(self) -> None:
        workspace_id = uuid.uuid4()
        jobs = [
            SimpleNamespace(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                platform="shop",
                sync_type="orders",
                status=SyncJobStatus.COMPLETED,
                items_synced=100,
                items_total=100,
                error_message=None,
                started_at=datetime(2026, 2, 26, tzinfo=UTC),
                completed_at=datetime(2026, 2, 26, tzinfo=UTC),
                created_at=datetime(2026, 2, 26, tzinfo=UTC),
            ),
        ]

        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = jobs
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        result_list = await service.list_recent_jobs(workspace_id, limit=10)

        assert len(result_list) == 1
        assert result_list[0]["platform"] == "shop"
        assert result_list[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_active_jobs(self) -> None:
        workspace_id = uuid.uuid4()
        jobs = [
            SimpleNamespace(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                platform="shop",
                sync_type="products",
                status=SyncJobStatus.RUNNING,
                items_synced=42,
                items_total=200,
                error_message=None,
                started_at=datetime(2026, 2, 26, tzinfo=UTC),
                completed_at=None,
                created_at=datetime(2026, 2, 26, tzinfo=UTC),
            ),
        ]

        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = jobs
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        active = await service.get_active_jobs(workspace_id)

        assert len(active) == 1
        assert active[0]["items_synced"] == 42
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/connect/test_sync_status_service.py -v`
Expected: FAIL with "No module named 'backend.modules.connect.services'"

**Step 3: Write minimal implementation**

Create `backend/modules/connect/services/__init__.py` (empty).

Create `backend/modules/connect/services/sync_status_service.py`:

```python
"""Service for tracking sync job progress."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import SyncJob, SyncJobStatus


class SyncStatusService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_sync_job(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        platform: str,
        sync_type: str,
    ) -> SyncJob:
        job = SyncJob(
            workspace_id=workspace_id,
            connected_account_id=connected_account_id,
            platform=platform,
            sync_type=sync_type,
            status=SyncJobStatus.PENDING,
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def start_job(self, job_id: uuid.UUID) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.status = SyncJobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        return job

    async def update_progress(
        self,
        job_id: uuid.UUID,
        items_synced: int,
        items_total: int | None = None,
    ) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.items_synced = items_synced
        if items_total is not None:
            job.items_total = items_total
        return job

    async def complete_job(self, job_id: uuid.UUID) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.status = SyncJobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        return job

    async def fail_job(self, job_id: uuid.UUID, error: str) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.status = SyncJobStatus.FAILED
        job.error_message = error
        job.completed_at = datetime.now(UTC)
        return job

    async def list_recent_jobs(
        self, workspace_id: uuid.UUID, limit: int = 20
    ) -> list[dict]:
        result = await self._session.execute(
            select(SyncJob)
            .where(SyncJob.workspace_id == workspace_id)
            .order_by(SyncJob.created_at.desc())
            .limit(limit)
        )
        jobs = result.scalars().all()
        return [self._serialize(j) for j in jobs]

    async def get_active_jobs(self, workspace_id: uuid.UUID) -> list[dict]:
        result = await self._session.execute(
            select(SyncJob)
            .where(SyncJob.workspace_id == workspace_id)
            .where(
                SyncJob.status.in_([SyncJobStatus.PENDING, SyncJobStatus.RUNNING])
            )
            .order_by(SyncJob.created_at.desc())
        )
        jobs = result.scalars().all()
        return [self._serialize(j) for j in jobs]

    @staticmethod
    def _serialize(job: SyncJob) -> dict:
        return {
            "id": str(job.id),
            "platform": job.platform,
            "sync_type": job.sync_type,
            "status": job.status.value if hasattr(job.status, "value") else job.status,
            "items_synced": job.items_synced,
            "items_total": job.items_total,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/connect/test_sync_status_service.py -v`
Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add backend/modules/connect/services/ tests/unit/connect/test_sync_status_service.py
git commit -m "feat(connect): add SyncStatusService for tracking sync job progress"
```

---

### Task 3: Scope Validation Utility

**Files:**
- Create: `backend/modules/connect/services/scope_validator.py`
- Test: `tests/unit/connect/test_scope_validator.py`

**Step 1: Write the failing test**

Create `tests/unit/connect/test_scope_validator.py`:

```python
"""Tests for platform scope validation."""

import pytest

from backend.modules.connect.services.scope_validator import (
    REQUIRED_SCOPES,
    validate_scopes,
)


class TestScopeValidation:
    def test_developer_all_scopes_present(self) -> None:
        granted = "user.info.basic,user.info.profile,user.info.stats,video.list,video.publish,video.upload,comment.list,comment.list.manage"
        result = validate_scopes("developer", granted)
        assert result["valid"] is True
        assert result["missing"] == []

    def test_developer_missing_scopes(self) -> None:
        granted = "user.info.basic,video.list"
        result = validate_scopes("developer", granted)
        assert result["valid"] is False
        assert "user.info.profile" in result["missing"]
        assert "video.publish" in result["missing"]

    def test_developer_empty_scopes(self) -> None:
        result = validate_scopes("developer", "")
        assert result["valid"] is False
        assert len(result["missing"]) == len(REQUIRED_SCOPES["developer"])

    def test_developer_none_scopes(self) -> None:
        result = validate_scopes("developer", None)
        assert result["valid"] is False

    def test_shop_always_valid(self) -> None:
        """Shop uses implicit scopes, always returns valid."""
        result = validate_scopes("shop", None)
        assert result["valid"] is True
        assert result["missing"] == []

    def test_marketing_always_valid(self) -> None:
        """Marketing uses implicit scopes, always returns valid."""
        result = validate_scopes("marketing", None)
        assert result["valid"] is True
        assert result["missing"] == []

    def test_unknown_platform(self) -> None:
        result = validate_scopes("unknown_platform", "some,scopes")
        assert result["valid"] is True
        assert result["missing"] == []

    def test_required_scopes_defined(self) -> None:
        assert "developer" in REQUIRED_SCOPES
        assert len(REQUIRED_SCOPES["developer"]) == 8
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/connect/test_scope_validator.py -v`
Expected: FAIL with "No module named"

**Step 3: Write minimal implementation**

Create `backend/modules/connect/services/scope_validator.py`:

```python
"""Validate granted OAuth scopes against required scopes per platform."""

from __future__ import annotations

REQUIRED_SCOPES: dict[str, list[str]] = {
    "developer": [
        "user.info.basic",
        "user.info.profile",
        "user.info.stats",
        "video.list",
        "video.publish",
        "video.upload",
        "comment.list",
        "comment.list.manage",
    ],
    # Shop and Marketing use implicit scopes (controlled at TikTok portal level)
}


def validate_scopes(platform: str, granted_scopes: str | None) -> dict:
    """Compare granted scopes against required scopes for a platform.

    Returns dict with 'valid' bool and 'missing' list of scope strings.
    """
    required = REQUIRED_SCOPES.get(platform)
    if not required:
        return {"valid": True, "missing": []}

    if not granted_scopes:
        return {"valid": False, "missing": required}

    granted_set = {s.strip() for s in granted_scopes.split(",") if s.strip()}
    missing = [s for s in required if s not in granted_set]
    return {"valid": len(missing) == 0, "missing": missing}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/connect/test_scope_validator.py -v`
Expected: PASS (8 tests)

**Step 5: Commit**

```bash
git add backend/modules/connect/services/scope_validator.py tests/unit/connect/test_scope_validator.py
git commit -m "feat(connect): add scope validation utility for platform OAuth scopes"
```

---

### Task 4: Sync Status API Routes

**Files:**
- Create: `backend/modules/connect/sync_routes.py`
- Test: `tests/unit/connect/test_sync_routes.py`

**Step 1: Write the failing test**

Create `tests/unit/connect/test_sync_routes.py`:

```python
"""Tests for sync status API routes."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient

from backend.main import app


class TestSyncStatusRoutes:
    @pytest.mark.asyncio
    @patch("backend.modules.connect.sync_routes.SyncStatusService")
    async def test_list_sync_jobs(self, MockService: MagicMock) -> None:
        from backend.auth.jwt import create_access_token

        mock_svc = AsyncMock()
        mock_svc.list_recent_jobs.return_value = [
            {
                "id": str(uuid.uuid4()),
                "platform": "shop",
                "sync_type": "orders",
                "status": "completed",
                "items_synced": 100,
                "items_total": 100,
                "error_message": None,
                "started_at": "2026-02-26T00:00:00+00:00",
                "completed_at": "2026-02-26T00:01:00+00:00",
                "created_at": "2026-02-26T00:00:00+00:00",
            }
        ]
        MockService.return_value = mock_svc

        token = create_access_token(user_id=uuid.uuid4())
        client = TestClient(app)
        workspace_id = uuid.uuid4()
        resp = client.get(
            f"/api/connect/sync/jobs?workspace_id={workspace_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["platform"] == "shop"

    @pytest.mark.asyncio
    @patch("backend.modules.connect.sync_routes.SyncStatusService")
    async def test_get_active_jobs(self, MockService: MagicMock) -> None:
        from backend.auth.jwt import create_access_token

        mock_svc = AsyncMock()
        mock_svc.get_active_jobs.return_value = []
        MockService.return_value = mock_svc

        token = create_access_token(user_id=uuid.uuid4())
        client = TestClient(app)
        workspace_id = uuid.uuid4()
        resp = client.get(
            f"/api/connect/sync/active?workspace_id={workspace_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    @patch("backend.modules.connect.sync_routes.SyncStatusService")
    async def test_trigger_manual_sync(self, MockService: MagicMock) -> None:
        from backend.auth.jwt import create_access_token

        mock_svc = AsyncMock()
        MockService.return_value = mock_svc

        # Mock connected account lookup
        with patch(
            "backend.modules.connect.sync_routes._get_connected_account"
        ) as mock_get:
            mock_account = MagicMock()
            mock_account.id = uuid.uuid4()
            mock_account.platform.value = "shop"
            mock_get.return_value = mock_account

            token = create_access_token(user_id=uuid.uuid4())
            client = TestClient(app)
            workspace_id = uuid.uuid4()
            resp = client.post(
                f"/api/connect/sync/trigger?workspace_id={workspace_id}&platform=shop",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert resp.status_code == 200
            assert resp.json()["status"] == "triggered"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/connect/test_sync_routes.py -v`
Expected: FAIL with "No module named 'backend.modules.connect.sync_routes'"

**Step 3: Write minimal implementation**

Create `backend/modules/connect/sync_routes.py`:

```python
"""API routes for sync status and manual sync triggers."""

from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from backend.db.models.platform import ConnectedAccount, Platform
from backend.dependencies import CurrentUser, DBSession
from backend.modules.connect.services.sync_status_service import SyncStatusService

router = APIRouter(prefix="/connect/sync", tags=["connect-sync"])


async def _get_connected_account(
    db: DBSession, workspace_id: uuid.UUID, platform: str
) -> ConnectedAccount | None:
    platform_enum = Platform(platform)
    result = await db.execute(
        select(ConnectedAccount)
        .where(ConnectedAccount.workspace_id == workspace_id)
        .where(ConnectedAccount.platform == platform_enum)
    )
    return result.scalar_one_or_none()


@router.get("/jobs")
async def list_sync_jobs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 20,
) -> list[dict]:
    service = SyncStatusService(db)
    return await service.list_recent_jobs(workspace_id, limit=limit)


@router.get("/active")
async def get_active_sync_jobs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = SyncStatusService(db)
    return await service.get_active_jobs(workspace_id)


@router.post("/trigger")
async def trigger_manual_sync(
    workspace_id: uuid.UUID,
    platform: Literal["shop", "developer", "marketing"],
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account = await _get_connected_account(db, workspace_id, platform)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No connected {platform} account found",
        )

    service = SyncStatusService(db)

    # Create sync jobs for each data type based on platform
    sync_types = _get_sync_types(platform)
    job_ids = []
    for sync_type in sync_types:
        job = await service.create_sync_job(
            workspace_id=workspace_id,
            connected_account_id=account.id,
            platform=platform,
            sync_type=sync_type,
        )
        job_ids.append(str(job.id))

    # TODO: Dispatch Celery tasks for each sync type
    # For now, just create the job records

    return {"status": "triggered", "job_ids": job_ids}


def _get_sync_types(platform: str) -> list[str]:
    """Return the sync types available for a platform."""
    if platform == "shop":
        return ["orders", "products"]
    elif platform == "marketing":
        return ["campaigns", "ad_groups", "ads"]
    elif platform == "developer":
        return ["videos"]
    return []
```

Then register this router in `backend/main.py`. Find where the connect router is included and add:

```python
from backend.modules.connect.sync_routes import router as sync_router
# Add near the other router includes:
app.include_router(sync_router, prefix="/api")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/connect/test_sync_routes.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/modules/connect/sync_routes.py tests/unit/connect/test_sync_routes.py backend/main.py
git commit -m "feat(connect): add sync status API routes (list, active, trigger)"
```

---

### Task 5: Connect WebSocket Endpoint

**Files:**
- Create: `backend/modules/connect/ws.py`
- Test: `tests/unit/connect/test_connect_ws.py`

**Step 1: Write the failing test**

Create `tests/unit/connect/test_connect_ws.py`:

```python
"""Tests for Connect WebSocket endpoint."""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient

from backend.main import app


class TestConnectWebSocketAuth:
    @pytest.mark.asyncio
    async def test_rejects_missing_token(self) -> None:
        client = TestClient(app)
        workspace_id = uuid.uuid4()

        with pytest.raises(Exception):
            with client.websocket_connect(f"/api/connect/ws/{workspace_id}"):
                pass

    @pytest.mark.asyncio
    async def test_rejects_invalid_token(self) -> None:
        client = TestClient(app)
        workspace_id = uuid.uuid4()

        with pytest.raises(Exception), client.websocket_connect(
            f"/api/connect/ws/{workspace_id}?token=invalid"
        ):
            pass


class TestConnectWebSocketMessages:
    @pytest.mark.asyncio
    @patch("backend.modules.connect.ws.get_redis")
    async def test_receives_sync_progress(self, mock_get_redis: AsyncMock) -> None:
        from backend.auth.jwt import create_access_token

        user_id = uuid.uuid4()
        token = create_access_token(user_id=user_id)
        workspace_id = uuid.uuid4()

        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        test_message = json.dumps(
            {
                "type": "sync_progress",
                "platform": "shop",
                "sync_type": "orders",
                "items_synced": 50,
                "items_total": 200,
            }
        )

        call_count = 0

        async def mock_get_message(ignore_subscribe_messages=True, timeout=1.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "message", "data": test_message.encode("utf-8")}
            return None

        mock_pubsub.get_message = mock_get_message
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_get_redis.return_value = mock_redis

        client = TestClient(app)
        with client.websocket_connect(
            f"/api/connect/ws/{workspace_id}?token={token}"
        ) as ws:
            data = ws.receive_text()
            parsed = json.loads(data)
            assert parsed["type"] == "sync_progress"
            assert parsed["items_synced"] == 50
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/connect/test_connect_ws.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `backend/modules/connect/ws.py`:

```python
"""WebSocket endpoint for real-time connect/sync updates."""

import asyncio
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError

from backend.auth.jwt import decode_token
from backend.tiktok.rate_limiter import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_ws_token(token: str) -> uuid.UUID | None:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


@router.websocket("/connect/ws/{workspace_id}")
async def connect_websocket(
    websocket: WebSocket,
    workspace_id: uuid.UUID,
) -> None:
    """WebSocket for real-time sync progress updates.

    Subscribes to Redis channel `connect:sync:{workspace_id}`.
    Messages include: sync_progress, sync_complete, sync_failed.
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    user_id = _validate_ws_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    channel = f"connect:sync:{workspace_id}"
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await websocket.send_text(data)

            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        logger.info("Connect WebSocket disconnected for workspace %s", workspace_id)
    except Exception:
        logger.exception("Connect WebSocket error for workspace %s", workspace_id)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
```

Register in `backend/main.py`:

```python
from backend.modules.connect.ws import router as connect_ws_router
app.include_router(connect_ws_router, prefix="/api")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/connect/test_connect_ws.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/modules/connect/ws.py tests/unit/connect/test_connect_ws.py backend/main.py
git commit -m "feat(connect): add WebSocket endpoint for real-time sync progress"
```

---

### Task 6: Workers Publish Sync Progress to Redis

**Files:**
- Create: `backend/modules/connect/services/sync_publisher.py`
- Modify: `backend/workers/data_sync.py`
- Test: `tests/unit/connect/test_sync_publisher.py`

**Step 1: Write the failing test**

Create `tests/unit/connect/test_sync_publisher.py`:

```python
"""Tests for sync progress publisher."""

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.connect.services.sync_publisher import publish_sync_event


class TestPublishSyncEvent:
    @pytest.mark.asyncio
    @patch("backend.modules.connect.services.sync_publisher.get_redis")
    async def test_publishes_progress_event(self, mock_get_redis: AsyncMock) -> None:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        workspace_id = uuid.uuid4()
        await publish_sync_event(
            workspace_id=workspace_id,
            event_type="sync_progress",
            platform="shop",
            sync_type="orders",
            items_synced=50,
            items_total=200,
        )

        mock_redis.publish.assert_called_once()
        channel = mock_redis.publish.call_args[0][0]
        assert channel == f"connect:sync:{workspace_id}"
        payload = json.loads(mock_redis.publish.call_args[0][1])
        assert payload["type"] == "sync_progress"
        assert payload["items_synced"] == 50

    @pytest.mark.asyncio
    @patch("backend.modules.connect.services.sync_publisher.get_redis")
    async def test_publishes_complete_event(self, mock_get_redis: AsyncMock) -> None:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        workspace_id = uuid.uuid4()
        await publish_sync_event(
            workspace_id=workspace_id,
            event_type="sync_complete",
            platform="shop",
            sync_type="orders",
            items_synced=200,
            items_total=200,
        )

        payload = json.loads(mock_redis.publish.call_args[0][1])
        assert payload["type"] == "sync_complete"
        assert payload["items_synced"] == 200
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/connect/test_sync_publisher.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `backend/modules/connect/services/sync_publisher.py`:

```python
"""Publish sync progress events to Redis for WebSocket consumption."""

from __future__ import annotations

import json
import uuid

from backend.tiktok.rate_limiter import get_redis


async def publish_sync_event(
    workspace_id: uuid.UUID,
    event_type: str,
    platform: str,
    sync_type: str,
    items_synced: int = 0,
    items_total: int | None = None,
    error: str | None = None,
) -> None:
    """Publish a sync event to the workspace's connect WebSocket channel."""
    channel = f"connect:sync:{workspace_id}"
    payload = {
        "type": event_type,
        "platform": platform,
        "sync_type": sync_type,
        "items_synced": items_synced,
        "items_total": items_total,
    }
    if error:
        payload["error"] = error

    r = await get_redis()
    await r.publish(channel, json.dumps(payload))
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/connect/test_sync_publisher.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add backend/modules/connect/services/sync_publisher.py tests/unit/connect/test_sync_publisher.py
git commit -m "feat(connect): add sync progress publisher for Redis/WebSocket events"
```

---

### Task 7: Frontend API Client & WebSocket Hook Updates

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Create: `frontend/src/hooks/useSyncWebSocket.ts`

**Step 1: Add API client methods**

Add to `frontend/src/lib/api.ts` after the existing connect functions (`listConnectedAccounts`):

```typescript
// Connect - Sync Status
export interface SyncJob {
  id: string;
  platform: string;
  sync_type: string;
  status: "pending" | "running" | "completed" | "failed";
  items_synced: number;
  items_total: number | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string | null;
}

export function listSyncJobs(
  workspaceId: string,
  token: string,
  limit = 20,
): Promise<SyncJob[]> {
  return apiFetch(`/connect/sync/jobs?workspace_id=${workspaceId}&limit=${limit}`, { token });
}

export function getActiveSyncJobs(
  workspaceId: string,
  token: string,
): Promise<SyncJob[]> {
  return apiFetch(`/connect/sync/active?workspace_id=${workspaceId}`, { token });
}

export function triggerManualSync(
  workspaceId: string,
  platform: string,
  token: string,
): Promise<{ status: string; job_ids: string[] }> {
  return apiFetch(`/connect/sync/trigger?workspace_id=${workspaceId}&platform=${platform}`, {
    method: "POST",
    token,
  });
}
```

**Step 2: Create WebSocket hook**

Create `frontend/src/hooks/useSyncWebSocket.ts`:

```typescript
"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api";

export interface SyncWSMessage {
  type: "sync_progress" | "sync_complete" | "sync_failed";
  platform: string;
  sync_type: string;
  items_synced: number;
  items_total: number | null;
  error?: string;
}

interface UseSyncWebSocketOptions {
  workspaceId: string;
  token: string | null;
  onMessage?: (message: SyncWSMessage) => void;
}

export function useSyncWebSocket({
  workspaceId,
  token,
  onMessage,
}: UseSyncWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (!token || !workspaceId) return;

    const url = `${WS_BASE}/connect/ws/${workspaceId}?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const message: SyncWSMessage = JSON.parse(event.data);
        onMessageRef.current?.(message);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => ws.close();
  }, [token, workspaceId]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { connected };
}
```

**Step 3: Verify frontend builds**

Run: `cd frontend && npx next build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/lib/api.ts frontend/src/hooks/useSyncWebSocket.ts
git commit -m "feat(connect): add sync status API client methods and WebSocket hook"
```

---

### Task 8: Redesigned Connect Page

**Files:**
- Modify: `frontend/src/app/(dashboard)/connect/page.tsx`
- Modify: `frontend/src/lib/api.ts` (add `getCurrentUser` if missing)

**Step 1: Read current user endpoint**

Check if there's an existing `/auth/me` endpoint that returns `workspace_id`. If not, we'll use the existing `getUserProfile` function. The key fix is replacing the hardcoded `"00000000-0000-0000-0000-000000000000"`.

Look at `frontend/src/lib/api.ts` for a `getUserProfile` or `getMe` function. If one exists, use it. If not, add:

```typescript
export function getCurrentUser(token: string): Promise<UserResponse> {
  return apiFetch("/auth/me", { token });
}
```

**Step 2: Rewrite connect page**

Replace `frontend/src/app/(dashboard)/connect/page.tsx` with:

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  getAuthorizeUrl,
  getCurrentUser,
  listConnectedAccounts,
  type ConnectedAccount,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { StatusBadge } from "@/components/ui/status-badge";
import { PageHeader } from "@/components/dashboard/page-header";

const PLATFORMS = [
  {
    id: "shop",
    name: "TikTok Shop",
    description: "Products, orders, fulfillment, returns, finance",
    icon: "🛍️",
    color: "bg-red-500",
    scopes: "Implicit (all 13 domains)",
  },
  {
    id: "developer",
    name: "TikTok Account",
    description: "Videos, comments, user profile, publishing",
    icon: "🎵",
    color: "bg-black",
    scopes: "8 scopes (user, video, comment)",
  },
  {
    id: "marketing",
    name: "TikTok Ads",
    description: "Campaigns, audiences, creatives, reporting",
    icon: "📊",
    color: "bg-blue-500",
    scopes: "Implicit (full Marketing API)",
  },
];

const STATUS_VARIANTS: Record<string, "success" | "danger" | "warning" | "neutral"> = {
  active: "success",
  error: "danger",
  disconnected: "neutral",
  refreshing: "warning",
};

export default function ConnectPage() {
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    getCurrentUser(token)
      .then((user) => {
        setWorkspaceId(user.workspace_id);
        return listConnectedAccounts(user.workspace_id, token);
      })
      .then(setAccounts)
      .catch((err) => toast.error(`Failed to load accounts: ${err.message}`))
      .finally(() => setLoading(false));
  }, []);

  async function handleConnect(platform: string) {
    const token = getAccessToken();
    if (!token || !workspaceId) return;

    try {
      const { authorize_url } = await getAuthorizeUrl(platform, workspaceId, token);
      window.location.href = authorize_url;
    } catch (err) {
      toast.error(`Failed to start connection: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
  }

  const connectedPlatforms = new Map(
    accounts.map((a) => [a.platform, a])
  );

  if (loading) {
    return (
      <div>
        <PageHeader title="Connect" description="Link your TikTok platform accounts." />
        <div className="flex justify-center py-12">
          <div className="animate-spin h-8 w-8 border-2 border-coral border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Connect"
        description="Link your TikTok platform accounts to manage everything from one place."
      />

      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-gray-500">
          {accounts.length} of {PLATFORMS.length} platforms connected
        </p>
        <Link
          href="/connect/status"
          className="text-sm text-coral hover:text-coral/80 font-medium"
        >
          View Sync Status →
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {PLATFORMS.map((platform) => {
          const account = connectedPlatforms.get(platform.id);
          const isConnected = !!account;
          return (
            <div
              key={platform.id}
              className="bg-white rounded-lg border border-gray-200 p-6 flex flex-col"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 ${platform.color} rounded-lg flex items-center justify-center text-lg`}>
                  {platform.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
                </div>
                {account && (
                  <StatusBadge status={account.status} variant={STATUS_VARIANTS[account.status] ?? "neutral"} />
                )}
              </div>

              <p className="text-sm text-gray-500 flex-1">{platform.description}</p>

              {account && (
                <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
                  <p className="font-medium">{account.platform_account_name || account.platform_account_id}</p>
                  <p className="text-gray-400 mt-0.5">Scopes: {platform.scopes}</p>
                </div>
              )}

              <button
                onClick={() => handleConnect(platform.id)}
                className={`mt-4 w-full py-2.5 px-4 rounded-md text-sm font-medium transition-colors ${
                  isConnected
                    ? "bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100"
                    : "bg-coral text-white hover:bg-coral/90"
                }`}
              >
                {isConnected ? "Reconnect" : "Connect"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

**Step 3: Verify frontend builds**

Run: `cd frontend && npx next build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/app/\(dashboard\)/connect/page.tsx frontend/src/lib/api.ts
git commit -m "feat(connect): redesign connect page with dynamic workspace ID, status badges, reconnect"
```

---

### Task 9: Post-Connect Sync Progress Page

**Files:**
- Create: `frontend/src/app/(dashboard)/connect/sync/page.tsx`

**Step 1: Create the sync progress page**

Create `frontend/src/app/(dashboard)/connect/sync/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getActiveSyncJobs, getCurrentUser, type SyncJob } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useSyncWebSocket, type SyncWSMessage } from "@/hooks/useSyncWebSocket";
import { PageHeader } from "@/components/dashboard/page-header";

interface SyncProgress {
  platform: string;
  sync_type: string;
  items_synced: number;
  items_total: number | null;
  status: "pending" | "running" | "completed" | "failed";
  error?: string;
}

export default function SyncProgressPage() {
  const router = useRouter();
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [progress, setProgress] = useState<Map<string, SyncProgress>>(new Map());
  const token = typeof window !== "undefined" ? getAccessToken() : null;

  useEffect(() => {
    if (!token) return;
    getCurrentUser(token).then((user) => {
      setWorkspaceId(user.workspace_id);
      // Load any active jobs
      getActiveSyncJobs(user.workspace_id, token).then((jobs) => {
        const initial = new Map<string, SyncProgress>();
        for (const job of jobs) {
          initial.set(`${job.platform}:${job.sync_type}`, {
            platform: job.platform,
            sync_type: job.sync_type,
            items_synced: job.items_synced,
            items_total: job.items_total,
            status: job.status,
          });
        }
        setProgress(initial);
      });
    });
  }, [token]);

  useSyncWebSocket({
    workspaceId: workspaceId || "",
    token,
    onMessage: (msg: SyncWSMessage) => {
      const key = `${msg.platform}:${msg.sync_type}`;
      setProgress((prev) => {
        const next = new Map(prev);
        next.set(key, {
          platform: msg.platform,
          sync_type: msg.sync_type,
          items_synced: msg.items_synced,
          items_total: msg.items_total,
          status: msg.type === "sync_complete" ? "completed" : msg.type === "sync_failed" ? "failed" : "running",
          error: msg.error,
        });
        return next;
      });
    },
  });

  const entries = Array.from(progress.values());
  const allCompleted = entries.length > 0 && entries.every((e) => e.status === "completed");
  const hasFailed = entries.some((e) => e.status === "failed");

  return (
    <div>
      <PageHeader
        title="Syncing Your Data"
        description="We're pulling your TikTok data into Frodo. This usually takes a few minutes."
      />

      {entries.length === 0 ? (
        <div className="text-center py-12">
          <div className="animate-spin h-8 w-8 border-2 border-coral border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Waiting for sync to start...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => {
            const pct = entry.items_total
              ? Math.round((entry.items_synced / entry.items_total) * 100)
              : null;

            return (
              <div
                key={`${entry.platform}:${entry.sync_type}`}
                className="bg-white rounded-lg border border-gray-200 p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-medium text-gray-900 capitalize">
                      {entry.platform}
                    </span>
                    <span className="text-gray-400 mx-2">·</span>
                    <span className="text-gray-600 capitalize">
                      {entry.sync_type.replace("_", " ")}
                    </span>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      entry.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : entry.status === "failed"
                          ? "bg-red-100 text-red-700"
                          : "bg-blue-100 text-blue-700"
                    }`}
                  >
                    {entry.status === "running" && pct !== null
                      ? `${pct}%`
                      : entry.status}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      entry.status === "completed"
                        ? "bg-green-500"
                        : entry.status === "failed"
                          ? "bg-red-500"
                          : "bg-coral"
                    }`}
                    style={{ width: `${pct ?? (entry.status === "completed" ? 100 : 10)}%` }}
                  />
                </div>

                <p className="text-xs text-gray-500 mt-1">
                  {entry.items_synced}
                  {entry.items_total ? ` / ${entry.items_total}` : ""} items synced
                </p>

                {entry.error && (
                  <p className="text-xs text-red-600 mt-1">{entry.error}</p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {allCompleted && (
        <div className="mt-8 text-center">
          <p className="text-green-600 font-medium mb-4">All data synced successfully!</p>
          <button
            onClick={() => router.push("/overview")}
            className="bg-coral text-white px-6 py-2.5 rounded-md font-medium hover:bg-coral/90"
          >
            Go to Dashboard
          </button>
        </div>
      )}

      {hasFailed && (
        <div className="mt-6 text-center">
          <p className="text-red-600 text-sm mb-2">Some syncs failed. You can retry from the sync status page.</p>
          <button
            onClick={() => router.push("/connect/status")}
            className="text-coral text-sm font-medium hover:text-coral/80"
          >
            View Sync Status →
          </button>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify frontend builds**

Run: `cd frontend && npx next build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/connect/sync/
git commit -m "feat(connect): add post-connect sync progress page with real-time WebSocket updates"
```

---

### Task 10: Sync Status Dashboard Page

**Files:**
- Create: `frontend/src/app/(dashboard)/connect/status/page.tsx`

**Step 1: Create the sync status dashboard**

Create `frontend/src/app/(dashboard)/connect/status/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";

import {
  getCurrentUser,
  listSyncJobs,
  triggerManualSync,
  type SyncJob,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageHeader } from "@/components/dashboard/page-header";
import { StatusBadge } from "@/components/ui/status-badge";

const PLATFORM_LABELS: Record<string, string> = {
  shop: "TikTok Shop",
  developer: "TikTok Account",
  marketing: "TikTok Ads",
};

const STATUS_VARIANTS: Record<string, "success" | "danger" | "warning" | "neutral"> = {
  completed: "success",
  failed: "danger",
  running: "warning",
  pending: "neutral",
};

export default function SyncStatusPage() {
  const [jobs, setJobs] = useState<SyncJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  async function loadJobs() {
    const token = getAccessToken();
    if (!token) return;

    try {
      const user = await getCurrentUser(token);
      setWorkspaceId(user.workspace_id);
      const data = await listSyncJobs(user.workspace_id, token, 50);
      setJobs(data);
    } catch (err) {
      toast.error("Failed to load sync history");
    } finally {
      setLoading(false);
    }
  }

  async function handleSyncNow(platform: string) {
    const token = getAccessToken();
    if (!token || !workspaceId) return;

    setSyncing(platform);
    try {
      await triggerManualSync(workspaceId, platform, token);
      toast.success(`Sync triggered for ${PLATFORM_LABELS[platform] ?? platform}`);
      // Reload jobs after a short delay
      setTimeout(loadJobs, 2000);
    } catch (err) {
      toast.error(`Failed to trigger sync: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setSyncing(null);
    }
  }

  // Group latest job per platform
  const latestByPlatform = new Map<string, SyncJob>();
  for (const job of jobs) {
    if (!latestByPlatform.has(job.platform)) {
      latestByPlatform.set(job.platform, job);
    }
  }

  return (
    <div>
      <PageHeader title="Sync Status" description="Monitor data sync health across all connected platforms." />

      {/* Platform health cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {["shop", "developer", "marketing"].map((platform) => {
          const latest = latestByPlatform.get(platform);
          return (
            <div key={platform} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">
                  {PLATFORM_LABELS[platform]}
                </h3>
                {latest && (
                  <StatusBadge
                    status={latest.status}
                    variant={STATUS_VARIANTS[latest.status] ?? "neutral"}
                  />
                )}
              </div>
              {latest ? (
                <div className="text-xs text-gray-500 space-y-1">
                  <p>Last sync: {latest.completed_at ? new Date(latest.completed_at).toLocaleString() : "In progress"}</p>
                  <p>Items: {latest.items_synced}{latest.items_total ? ` / ${latest.items_total}` : ""}</p>
                  {latest.error_message && (
                    <p className="text-red-600">{latest.error_message}</p>
                  )}
                </div>
              ) : (
                <p className="text-xs text-gray-400">No sync history</p>
              )}
              <button
                onClick={() => handleSyncNow(platform)}
                disabled={syncing === platform}
                className="mt-3 w-full py-1.5 px-3 text-xs font-medium rounded-md border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                {syncing === platform ? "Syncing..." : "Sync Now"}
              </button>
            </div>
          );
        })}
      </div>

      {/* Sync history table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Sync History</h3>
          <button
            onClick={loadJobs}
            className="text-xs text-coral hover:text-coral/80 font-medium"
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin h-6 w-6 border-2 border-coral border-t-transparent rounded-full" />
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            No sync jobs yet. Connect a platform to get started.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  <th className="px-4 py-2 text-left">Platform</th>
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Status</th>
                  <th className="px-4 py-2 text-right">Items</th>
                  <th className="px-4 py-2 text-left">Started</th>
                  <th className="px-4 py-2 text-left">Completed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium text-gray-900">
                      {PLATFORM_LABELS[job.platform] ?? job.platform}
                    </td>
                    <td className="px-4 py-2 text-gray-600 capitalize">
                      {job.sync_type.replace("_", " ")}
                    </td>
                    <td className="px-4 py-2">
                      <StatusBadge
                        status={job.status}
                        variant={STATUS_VARIANTS[job.status] ?? "neutral"}
                      />
                    </td>
                    <td className="px-4 py-2 text-right text-gray-600">
                      {job.items_synced}
                      {job.items_total ? ` / ${job.items_total}` : ""}
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-xs">
                      {job.started_at ? new Date(job.started_at).toLocaleString() : "—"}
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-xs">
                      {job.completed_at ? new Date(job.completed_at).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
```

**Step 2: Verify frontend builds**

Run: `cd frontend && npx next build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/connect/status/
git commit -m "feat(connect): add sync status dashboard with health cards, history table, manual sync"
```

---

### Task 11: OAuth Callback Redirect to Sync Page

**Files:**
- Modify: `backend/modules/connect/routes.py`

**Step 1: Update callbacks to redirect to frontend sync page**

Currently the 3 callbacks (`shop_callback`, `developer_callback`, `marketing_callback`) return JSON. For browser-based OAuth flow, they should redirect the user to the frontend sync progress page.

Add a helper at the top of `routes.py`:

```python
from fastapi.responses import RedirectResponse

FRONTEND_URL = settings.frontend_url  # e.g. "http://localhost:3000"
```

Add `frontend_url` to `backend/config.py` if it doesn't exist:
```python
frontend_url: str = "http://localhost:3000"
```

Then at the end of each callback, instead of returning `ConnectedAccountResponse`, add a redirect:

For `shop_callback`, after `db.add(token_vault)`:
```python
    # Trigger initial sync for the new connection
    # TODO: dispatch Celery initial sync tasks here

    return RedirectResponse(
        url=f"{FRONTEND_URL}/connect/sync?platform=shop&account_id={account.id}",
        status_code=303,
    )
```

Apply the same pattern to `developer_callback` and `marketing_callback`, changing `platform=` accordingly.

**Step 2: Run tests to check nothing breaks**

Run: `python -m pytest tests/ -v --tb=short -q`
Expected: All existing tests pass (callbacks in tests may need mock adjustments if they check response body)

**Step 3: Commit**

```bash
git add backend/modules/connect/routes.py backend/config.py
git commit -m "feat(connect): redirect OAuth callbacks to frontend sync progress page"
```

---

### Task 12: Full Test Suite Verification

**Step 1: Run all backend tests**

Run: `python -m pytest --tb=short -q`
Expected: All tests pass (879+ tests)

**Step 2: Run frontend build**

Run: `cd frontend && npx next build`
Expected: Build succeeds with no errors

**Step 3: Final commit (if any formatting fixes needed)**

```bash
cd /Users/amitkolton/Projects/Tiktok\ Frodo
black backend/
isort backend/
git add -u && git commit -m "chore: formatting fixes for connect pipeline overhaul"
```

---

## Summary of All Files

**Created (10 files):**
- `backend/modules/connect/services/__init__.py`
- `backend/modules/connect/services/sync_status_service.py`
- `backend/modules/connect/services/scope_validator.py`
- `backend/modules/connect/services/sync_publisher.py`
- `backend/modules/connect/sync_routes.py`
- `backend/modules/connect/ws.py`
- `frontend/src/hooks/useSyncWebSocket.ts`
- `frontend/src/app/(dashboard)/connect/sync/page.tsx`
- `frontend/src/app/(dashboard)/connect/status/page.tsx`
- `tests/unit/connect/__init__.py`

**Modified (5 files):**
- `backend/db/models/platform.py` — Added `SyncJobStatus` enum and `SyncJob` model
- `backend/modules/connect/routes.py` — Callback redirects to frontend sync page
- `backend/main.py` — Register sync_routes and connect_ws routers
- `frontend/src/lib/api.ts` — Added sync status API functions + `getCurrentUser`
- `frontend/src/app/(dashboard)/connect/page.tsx` — Full redesign

**Test files created (5 files):**
- `tests/unit/connect/__init__.py`
- `tests/unit/connect/test_sync_job_model.py`
- `tests/unit/connect/test_sync_status_service.py`
- `tests/unit/connect/test_scope_validator.py`
- `tests/unit/connect/test_sync_routes.py`
- `tests/unit/connect/test_connect_ws.py`
- `tests/unit/connect/test_sync_publisher.py`
