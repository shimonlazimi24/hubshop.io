import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.content.schemas import (
    CompareVideosRequest,
    CreatorInfoResponse,
    QueryVideosRequest,
    VideoDetailResponse,
    VideoMetricsResponse,
    VideoPerformanceSummary,
    VideoSummaryResponse,
)
from backend.modules.content.services.video_service import VideoService

router = APIRouter()


@router.get(
    "/videos",
    response_model=PaginatedResponse[VideoSummaryResponse],
)
async def list_videos(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[VideoSummaryResponse]:
    service = VideoService(db)
    result = await service.list_videos(
        workspace_id,
        status_filter=status_filter,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[VideoSummaryResponse.model_validate(v) for v in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/videos/top", response_model=list[VideoSummaryResponse])
async def get_top_videos(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    metric: str = "view_count",
    limit: int = 10,
) -> list[VideoSummaryResponse]:
    service = VideoService(db)
    videos = await service.get_top_videos(workspace_id, metric=metric, limit=limit)
    return [VideoSummaryResponse.model_validate(v) for v in videos]


@router.get("/videos/performance-summary")
async def get_performance_summary(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = VideoService(db)
    return await service.get_video_performance_summary(workspace_id)


@router.post("/videos/compare")
async def compare_videos(
    workspace_id: uuid.UUID,
    body: CompareVideosRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = VideoService(db)
    video_uuids = [uuid.UUID(vid) for vid in body.video_ids]
    comparisons = await service.compare_video_performance(video_uuids)
    return {"comparisons": comparisons}


@router.get(
    "/videos/{video_id}",
    response_model=VideoDetailResponse,
)
async def get_video(
    video_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> VideoDetailResponse:
    service = VideoService(db)
    video = await service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    return VideoDetailResponse.model_validate(video)


@router.get(
    "/videos/{video_id}/metrics",
    response_model=list[VideoMetricsResponse],
)
async def get_video_metrics(
    video_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[VideoMetricsResponse]:
    service = VideoService(db)
    video = await service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    metrics = await service.get_video_metrics(video_id)
    return [VideoMetricsResponse.model_validate(m) for m in metrics]


@router.post("/videos/sync")
async def sync_videos(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = VideoService(db)
    count = await service.sync_videos(workspace_id)
    return {"synced": count}


@router.get("/creator-info", response_model=CreatorInfoResponse)
async def get_creator_info(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = VideoService(db)
    return await service.get_creator_info(workspace_id)


@router.post("/videos/query")
async def query_videos(
    workspace_id: uuid.UUID,
    body: QueryVideosRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = VideoService(db)
    videos = await service.query_videos_by_id(workspace_id, body.video_ids)
    return {"videos": videos}
