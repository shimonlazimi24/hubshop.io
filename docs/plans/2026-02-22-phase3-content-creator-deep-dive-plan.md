# Phase 3: Content & Creator Deep-Dive Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deep-dive the Content and Creator modules from surface-level to production-grade, adding comment management, photo posting, video query, metrics benchmarking, creator route expansion, TTCM save flows, and cross-module integration.

**Architecture:** Content module uses Developer API (`_get_developer_gateway` → `(ConnectedAccount, PlatformGateway)` with `TikTokDeveloperClient`). Creator discovery uses Marketing API (`_get_marketing_gateway` → `PlatformGateway` with `TikTokMarketingClient`). Both persist data locally in PostgreSQL via SQLAlchemy async. Routes follow FastAPI pattern with `CurrentUser` + `DBSession` dependencies.

**Tech Stack:** Python 3.12+ / FastAPI / SQLAlchemy async / pytest / TikTok Developer API + Marketing API

**Baseline:** 781 tests passing, Content has 9 routes + 2 services, Creators has 14 routes + 6 services

---

## Current State Summary

### Content Module
- **VideoService** (7 methods): list_videos, get_video, get_video_metrics, sync_videos, publish_video, get_publish_status, get_creator_info
- **PublishService** (6 methods): create_publish_job, get_publish_job, list_publish_jobs, update_publish_status, check_and_update_publish_status, get_calendar_entries
- **Routes**: 5 video routes, 3 publish routes, 1 calendar route = **9 total**
- **DB Models**: Video, VideoMetrics, ContentPublishJob, ContentSyncCursor
- **Gaps**: No comment management, no photo posting, no video query-by-ID, no metrics benchmarking

### Creators Module
- **CreatorService** (5 methods): search_creators, get_creator, save_creator, get_creator_videos, sync_creator_metrics
- **CreatorProfileService** (4 methods): list_creators, get_creator, save_creator, upsert_creator_from_api
- **CreatorDiscoveryService** (3 methods): search_creators, get_creator_info, get_creator_audience
- **CreatorCampaignService** (7 methods): list_campaigns, get_campaign, create_campaign, update_campaign, list_invitations, invite_creator, update_invitation_status (via campaign_service.py)
- **SparkAdsService** (3 methods): request_authorization, list_authorizations, check_authorization_status
- **PartnershipService**: Duplicate of CampaignService — needs cleanup
- **Routes**: profiles (3), discovery (3), campaigns (6), spark_ads (2) = **14 total**
- **Gaps**: No metrics sync route, no creator videos route, no auth status check route, no invitation status update route, PartnershipService is dead code

---

### Task 1: Content — Comment Service (Model + Service)

**Files:**
- Create: `backend/modules/content/services/comment_service.py`
- Modify: `backend/db/models/content.py` (add Comment model)
- Test: `tests/unit/content/test_comment_service.py`

**Context:**
TikTok Developer API provides comment endpoints at `comment.list` and `comment.list.manage` scopes:
- `POST /v2/video/comment/list/` — list comments on a video (fields: id, text, create_time, like_count, reply_count, parent_comment_id)
- `POST /v2/video/comment/reply/create/` — reply to a comment
- `POST /v2/video/comment/delete/` — delete a comment

The service follows the same `_get_developer_gateway(workspace_id)` pattern as VideoService.

**Step 1: Add Comment model to content.py**

Add to `backend/db/models/content.py`:
```python
class Comment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "comments"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_comment_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    parent_comment_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Platform ID of parent comment for replies",
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    author_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    comment_create_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_comments_video_parent", "video_id", "parent_comment_id"),
    )
```

**Step 2: Create CommentService**

Create `backend/modules/content/services/comment_service.py` with methods:
- `list_comments(workspace_id, video_id, *, page, page_size)` → PaginatedResult[Comment] from DB
- `sync_comments(workspace_id, video: Video)` → int — fetch from Developer API `POST /v2/video/comment/list/` and upsert
- `reply_to_comment(workspace_id, video: Video, comment_id: str, text: str)` → dict — call Developer API `POST /v2/video/comment/reply/create/`
- `delete_comment(workspace_id, video: Video, comment_id: str)` → bool — call Developer API `POST /v2/video/comment/delete/`
- `_upsert_comment(video_id, workspace_id, comment_data)` → Comment

The service reuses `_get_developer_gateway(workspace_id)` from the same pattern as VideoService (copy the private method).

**Step 3: Write tests**

10 tests covering: list_comments pagination, sync_comments API call, sync_comments upsert existing, reply_to_comment, delete_comment, list with parent filter, empty result handling, sync pagination (has_more), comment model creation, _upsert_comment update path.

**Step 4: Run tests, verify pass, commit**

```bash
pytest tests/unit/content/test_comment_service.py -v
git add backend/db/models/content.py backend/modules/content/services/comment_service.py tests/unit/content/test_comment_service.py
git commit -m "feat: add comment model and service for content module"
```

---

### Task 2: Content — Comment Routes + Schemas

**Files:**
- Create: `backend/modules/content/routes/comments.py`
- Modify: `backend/modules/content/schemas.py` (add comment schemas)
- Modify: `backend/modules/content/routes/__init__.py` (register comments router)
- Test: `tests/unit/content/test_comment_routes.py`

**Step 1: Add comment schemas to schemas.py**

Append to `backend/modules/content/schemas.py`:
```python
# --- Comments ---

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_comment_id: str
    parent_comment_id: str | None = None
    text: str
    like_count: int
    reply_count: int
    author_username: str | None = None
    author_avatar_url: str | None = None
    comment_create_time: datetime | None = None
    created_at: datetime

class ReplyToCommentRequest(BaseModel):
    text: str
```

**Step 2: Create comments routes**

Create `backend/modules/content/routes/comments.py` with routes:
- `GET /videos/{video_id}/comments` → PaginatedResponse[CommentResponse] (list comments)
- `POST /videos/{video_id}/comments/sync` → {"synced": int} (sync from API)
- `POST /videos/{video_id}/comments/{comment_id}/reply` → dict (reply)
- `DELETE /videos/{video_id}/comments/{comment_id}` → {"deleted": True} (delete)

**Step 3: Register in routes/__init__.py**

Add `from backend.modules.content.routes.comments import router as comments_router` and `router.include_router(comments_router)`.

**Step 4: Write 8 route tests**

Tests: list_comments route, sync route, reply route, delete route, list with pagination, 404 on missing video, empty comments list, sync returns count.

**Step 5: Run tests, commit**

```bash
pytest tests/unit/content/test_comment_routes.py -v
```

---

### Task 3: Content — Photo Posting + Video Query

**Files:**
- Modify: `backend/modules/content/services/video_service.py` (add query_videos_by_id)
- Modify: `backend/modules/content/services/publish_service.py` (add create_photo_publish_job)
- Modify: `backend/modules/content/schemas.py` (add photo schemas)
- Modify: `backend/modules/content/routes/videos.py` (add query route)
- Modify: `backend/modules/content/routes/publish.py` (add photo route)
- Test: `tests/unit/content/test_photo_publish.py`

**Step 1: Add query_videos_by_id to VideoService**

```python
async def query_videos_by_id(
    self, workspace_id: uuid.UUID, video_ids: list[str]
) -> list[dict]:
    """Query specific videos by their platform IDs via Developer API."""
    _, gateway = await self._get_developer_gateway(workspace_id)
    resp = await gateway.post(
        "/video/query/",
        json_body={"filters": {"video_ids": video_ids}},
        params={"fields": "id,title,video_description,cover_image_url,embed_link,duration,create_time,like_count,comment_count,share_count,view_count"},
    )
    return resp.get("data", {}).get("videos", [])
```

**Step 2: Add create_photo_publish_job to PublishService**

```python
async def create_photo_publish_job(
    self,
    workspace_id: uuid.UUID,
    *,
    photo_urls: list[str],
    title: str | None = None,
    description: str | None = None,
    privacy_level: str = "PUBLIC_TO_EVERYONE",
    disable_comment: bool = False,
    auto_add_music: bool = True,
    photo_cover_index: int = 0,
) -> ContentPublishJob:
    """Create a photo post via Developer API."""
    account, gateway = await self._get_developer_gateway(workspace_id)
    body = {
        "post_info": {
            "title": title or "",
            "description": description or "",
            "disable_comment": disable_comment,
            "privacy_level": privacy_level,
            "auto_add_music": auto_add_music,
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "photo_cover_index": photo_cover_index,
            "photo_images": photo_urls,
        },
        "post_mode": "DIRECT_POST",
        "media_type": "PHOTO",
    }
    resp = await gateway.post("/post/publish/content/init/", json_body=body)
    data = resp.get("data", {})
    publish_id = data.get("publish_id", "")

    job = ContentPublishJob(
        workspace_id=workspace_id,
        connected_account_id=account.id,
        publish_id=publish_id,
        title=title,
        video_url=None,
        privacy_level=privacy_level,
        status="PENDING",
        disable_comment=disable_comment,
    )
    self._session.add(job)
    await self._session.flush()
    return job
```

**Step 3: Add schemas**

```python
class PublishPhotoRequest(BaseModel):
    photo_urls: list[str]
    title: str | None = None
    description: str | None = None
    privacy_level: str = "PUBLIC_TO_EVERYONE"
    disable_comment: bool = False
    auto_add_music: bool = True
    photo_cover_index: int = 0

class QueryVideosRequest(BaseModel):
    video_ids: list[str]
```

**Step 4: Add routes**

In `videos.py`: `POST /videos/query` → list of video dicts
In `publish.py`: `POST /publish/photo` → ContentPublishJobResponse

**Step 5: Write 10 tests**

Tests: query_videos_by_id success, query empty list, publish_photo success, publish_photo creates job record, photo with multiple URLs, photo with title, video query API call format, publish photo API call format, query videos route, publish photo route.

**Step 6: Run tests, commit**

---

### Task 4: Content — Video Metrics Benchmarking

**Files:**
- Modify: `backend/modules/content/services/video_service.py` (add metrics methods)
- Modify: `backend/modules/content/schemas.py` (add benchmark schemas)
- Modify: `backend/modules/content/routes/videos.py` (add benchmark routes)
- Test: `tests/unit/content/test_video_benchmarks.py`

**Step 1: Add benchmarking methods to VideoService**

```python
async def get_top_videos(
    self, workspace_id: uuid.UUID, *, metric: str = "view_count", limit: int = 10
) -> list[Video]:
    """Get top performing videos by a specific metric."""
    # metric must be one of: view_count, like_count, comment_count, share_count
    ...

async def get_video_performance_summary(
    self, workspace_id: uuid.UUID
) -> dict:
    """Aggregate performance summary across all workspace videos."""
    # Returns: total_videos, total_views, total_likes, total_comments, total_shares,
    #          avg_views, avg_likes, avg_engagement_rate

async def compare_video_performance(
    self, video_ids: list[uuid.UUID]
) -> list[dict]:
    """Compare metrics across multiple videos for benchmarking."""
    # Returns list of {video_id, title, view_count, like_count, ...} for comparison
```

**Step 2: Add schemas**

```python
class VideoPerformanceSummary(BaseModel):
    total_videos: int
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    avg_views: float
    avg_likes: float
    avg_engagement_rate: float

class TopVideosRequest(BaseModel):
    metric: str = "view_count"
    limit: int = 10
```

**Step 3: Add routes**

- `GET /videos/top?metric=view_count&limit=10` → list[VideoSummaryResponse]
- `GET /videos/performance-summary` → VideoPerformanceSummary
- `POST /videos/compare` → list of video dicts with metrics

**Step 4: Write 10 tests**

Tests: top_videos by views, top_videos by likes, top_videos limit, performance_summary calculation, performance_summary empty workspace, compare_videos, compare_videos partial, engagement_rate calc, top_videos route, performance_summary route.

**Step 5: Run tests, commit**

---

### Task 5: Creator — Service Consolidation + Cleanup

**Files:**
- Delete: `backend/modules/creators/services/partnership_service.py`
- Modify: `backend/modules/creators/services/creator_service.py` (add missing methods)
- Modify: `backend/modules/creators/services/campaign_service.py` (add update_invitation_status)
- Test: `tests/unit/creators/test_creator_service_expanded.py`

**Step 1: Delete PartnershipService**

Remove `partnership_service.py` — it duplicates CampaignService.

**Step 2: Add methods to CreatorCampaignService (campaign_service.py)**

Ensure `update_invitation_status` exists:
```python
async def update_invitation_status(
    self, invitation_id: uuid.UUID, *, status: str, responded_at: datetime | None = None
) -> CreatorInvitation | None:
    """Update invitation status (ACCEPTED, DECLINED, EXPIRED)."""
    result = await self._session.execute(
        select(CreatorInvitation).where(CreatorInvitation.id == invitation_id)
    )
    invitation = result.scalar_one_or_none()
    if invitation:
        invitation.status = status
        if responded_at:
            invitation.responded_at = responded_at
    return invitation
```

Also add `get_campaign_stats`:
```python
async def get_campaign_stats(self, campaign_id: uuid.UUID) -> dict:
    """Get invitation stats for a campaign."""
    # Returns: total_invitations, pending, accepted, declined, total_offered, acceptance_rate
```

**Step 3: Add sync_creator_to_workspace to CreatorService**

```python
async def sync_creator_to_workspace(
    self, workspace_id: uuid.UUID, creator_data: dict
) -> CreatorProfile:
    """Save a creator from TTCM discovery results into the workspace."""
    from backend.modules.creators.services.creator_profile_service import CreatorProfileService
    profile_service = CreatorProfileService(self._session)
    return await profile_service.upsert_creator_from_api(workspace_id, creator_data)
```

**Step 4: Write 10 tests**

Tests: update_invitation_status, update to accepted, update nonexistent, get_campaign_stats, campaign_stats empty, campaign_stats with mixed statuses, sync_creator_to_workspace, sync_creator_update existing, partnership_service deleted, creator service delegation.

**Step 5: Run tests, commit**

---

### Task 6: Creator — Routes Expansion

**Files:**
- Modify: `backend/modules/creators/routes_profiles.py` (add metrics sync, videos)
- Modify: `backend/modules/creators/routes_spark_ads.py` (add auth status check)
- Modify: `backend/modules/creators/routes_campaigns.py` (add invitation update, campaign stats)
- Modify: `backend/modules/creators/routes_discovery.py` (add save-to-workspace)
- Modify: `backend/modules/creators/schemas.py` (add new schemas)
- Test: `tests/unit/creators/test_creator_routes_expanded.py`

**Step 1: Add schemas**

```python
class UpdateInvitationStatusRequest(BaseModel):
    status: str  # ACCEPTED, DECLINED

class CampaignStatsResponse(BaseModel):
    total_invitations: int
    pending: int
    accepted: int
    declined: int
    total_offered_amount: str | None = None
    acceptance_rate: float

class SaveCreatorRequest(BaseModel):
    creator_data: dict  # Raw data from TTCM discovery
```

**Step 2: Add routes**

In `routes_profiles.py`:
- `POST /profiles/{creator_id}/sync-metrics` → CreatorDetailResponse (calls sync_creator_metrics)
- `GET /profiles/{creator_id}/videos` → list[dict] (calls get_creator_videos)

In `routes_spark_ads.py`:
- `POST /spark-ads/authorizations/{auth_id}/check` → ContentAuthorizationResponse

In `routes_campaigns.py`:
- `PUT /campaigns/{campaign_id}/invitations/{invitation_id}/status` → CreatorInvitationResponse
- `GET /campaigns/{campaign_id}/stats` → CampaignStatsResponse

In `routes_discovery.py`:
- `POST /discover/save` → CreatorProfileResponse (save TTCM result to workspace)

**Step 3: Write 10 tests**

Tests: sync_metrics_route, get_creator_videos_route, check_auth_status_route, update_invitation_status_route, campaign_stats_route, save_creator_from_discovery_route, sync_metrics_404, check_auth_pending, campaign_stats_empty, save_creator_creates_profile.

**Step 4: Run tests, commit**

---

### Task 7: Content — Commercial Content & Ad Library Service

**Files:**
- Create: `backend/modules/content/services/commercial_content_service.py`
- Modify: `backend/modules/content/schemas.py` (add commercial content schemas)
- Create: `backend/modules/content/routes/commercial.py`
- Modify: `backend/modules/content/routes/__init__.py` (register)
- Test: `tests/unit/content/test_commercial_content.py`

**Context:**
The Commercial Content API (Research API family, scope `research.adlib.basic`) provides:
- `POST /research/adlib/ad/query/` — search ads
- `POST /research/adlib/advertiser/query/` — search advertisers
- `POST /research/adlib/ad/detail/` — get ad details
- `POST /research/adlib/ad/report/` — get ad reports
- `POST /research/adlib/commercial_content/query/` — search branded content

This uses the Developer API gateway but with a **client access token** (not user token). The service will use `_get_developer_gateway` if configured for research scopes.

**Step 1: Create CommercialContentService**

```python
class CommercialContentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_ads(self, workspace_id, *, search_term, date_range, country_code="ALL", max_count=20, search_id=None) -> dict
    async def search_advertisers(self, workspace_id, *, search_term, max_count=20) -> dict
    async def get_ad_detail(self, workspace_id, *, ad_id) -> dict
    async def get_ad_report(self, workspace_id, *, date_range, country_code="ALL") -> dict
    async def search_commercial_content(self, workspace_id, *, date_range, creator_usernames=None, max_count=20, search_id=None) -> dict
```

**Step 2: Add schemas + routes**

5 routes under `/content/commercial/`:
- `POST /commercial/ads/search`
- `POST /commercial/advertisers/search`
- `POST /commercial/ads/{ad_id}/detail`
- `POST /commercial/ads/report`
- `POST /commercial/content/search`

**Step 3: Write 8 tests**

Tests: search_ads, search_advertisers, get_ad_detail, get_ad_report, search_commercial_content, search_ads with pagination, search_ads with country filter, search_commercial_content with creator filter.

**Step 4: Run tests, commit**

---

### Task 8: Creator — Spark Ads Deep-Dive + Performance Reporting

**Files:**
- Modify: `backend/modules/creators/services/spark_ads_service.py` (add cancel, get code)
- Modify: `backend/modules/creators/services/creator_service.py` (add performance reporting)
- Modify: `backend/modules/creators/routes_spark_ads.py` (add routes)
- Modify: `backend/modules/creators/routes_profiles.py` (add performance route)
- Modify: `backend/modules/creators/schemas.py` (add schemas)
- Test: `tests/unit/creators/test_spark_ads_expanded.py`

**Step 1: Expand SparkAdsService**

```python
async def cancel_authorization(self, authorization_id: uuid.UUID) -> ContentAuthorization | None:
    """Cancel/revoke a pending authorization."""

async def get_authorization_code(self, authorization_id: uuid.UUID) -> str | None:
    """Get the Spark Ads authorization code for an approved auth."""

async def list_authorized_videos(self, workspace_id: uuid.UUID) -> list[ContentAuthorization]:
    """List all approved authorizations with valid codes."""
```

**Step 2: Add creator performance to CreatorService**

```python
async def get_creator_performance(self, creator_id: uuid.UUID) -> dict:
    """Get performance metrics for a saved creator."""
    # Returns: follower_count, engagement_rate, video_count, tier, avg_likes_per_video
```

**Step 3: Add routes**

- `POST /spark-ads/authorizations/{auth_id}/cancel` → ContentAuthorizationResponse
- `GET /spark-ads/authorizations/{auth_id}/code` → {"authorization_code": str}
- `GET /spark-ads/authorized-videos` → list[ContentAuthorizationResponse]
- `GET /profiles/{creator_id}/performance` → dict

**Step 4: Write 10 tests**

Tests: cancel_authorization, cancel_nonexistent, get_code_approved, get_code_pending_returns_none, list_authorized_videos, list_authorized_empty, creator_performance, creator_performance_metrics, cancel_route, authorized_videos_route.

**Step 5: Run tests, commit**

---

### Task 9: Content + Creator — Cross-Module Integration

**Files:**
- Create: `backend/modules/content/services/content_creator_bridge.py`
- Modify: `backend/modules/content/routes/__init__.py`
- Modify: `backend/modules/content/schemas.py`
- Test: `tests/unit/content/test_content_creator_bridge.py`

**Context:**
This task creates the bridge between content videos and creator Spark Ads flows. When a brand sees a creator's video they want to use as a Spark Ad, they need to:
1. View the video (content module)
2. Request Spark Ads authorization (creators module)
3. Link authorization to content for use in ad campaigns

**Step 1: Create ContentCreatorBridge service**

```python
class ContentCreatorBridge:
    """Bridge service linking content videos to creator Spark Ads flows."""

    async def get_video_with_creator(self, video_id, workspace_id) -> dict:
        """Get video details along with associated creator profile."""

    async def request_spark_ad_for_video(self, workspace_id, video_id, creator_id) -> ContentAuthorization:
        """Create Spark Ads request for a specific video-creator pair."""

    async def get_creator_content_summary(self, workspace_id, creator_id) -> dict:
        """Get summary of a creator's content + authorization status."""
```

**Step 2: Add routes**

- `GET /content/videos/{video_id}/creator` → dict (video + creator info)
- `POST /content/videos/{video_id}/spark-ad-request` → ContentAuthorizationResponse
- `GET /content/creators/{creator_id}/content-summary` → dict

**Step 3: Write 8 tests**

Tests: get_video_with_creator, request_spark_ad, creator_content_summary, video_not_found, creator_not_found, spark_ad_creates_auth, content_summary_empty, content_summary_with_videos.

**Step 4: Run tests, commit**

---

### Task 10: Regression Testing + Route Count Verification

**Files:**
- No new files

**Step 1: Run full test suite**

```bash
pytest --tb=short -q
```

Expected: All tests pass (781 baseline + ~86 new = ~867+ total)

**Step 2: Verify content routes**

```bash
python -c "
from backend.modules.content.routes import router
print(f'Content routes: {len(router.routes)}')
for r in router.routes:
    print(f'  {r.methods} {r.path}')
"
```

Expected: ~22+ content routes (was 9)

**Step 3: Verify creator routes**

```bash
python -c "
from backend.modules.creators.routes import router
print(f'Creator routes: {len(router.routes)}')
for r in router.routes:
    print(f'  {r.methods} {r.path}')
"
```

Expected: ~24+ creator routes (was 14)

**Step 4: Verify no import errors**

```bash
python -c "from backend.main import create_app; print('OK')"
```

---

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Tests | 781 | ~867+ |
| Content routes | 9 | ~22+ |
| Creator routes | 14 | ~24+ |
| Content services | 2 | 4 (+ CommentService, CommercialContentService) |
| Creator services | 6 | 5 (consolidated, -PartnershipService) |
| New DB models | 0 | 1 (Comment) |
| New service methods | 0 | ~35+ |
