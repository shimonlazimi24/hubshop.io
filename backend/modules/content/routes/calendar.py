import uuid

from fastapi import APIRouter, Query

from backend.dependencies import CurrentUser, DBSession
from backend.modules.content.schemas import CalendarEntry, VideoSummaryResponse
from backend.modules.content.services.publish_service import PublishService

router = APIRouter()


@router.get(
    "/calendar",
    response_model=list[CalendarEntry],
)
async def get_calendar(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    year: int = Query(..., ge=2020, le=2100, description="Calendar year"),
    month: int = Query(..., ge=1, le=12, description="Calendar month"),
) -> list[CalendarEntry]:
    service = PublishService(db)
    entries = await service.get_calendar_entries(workspace_id, year, month)

    # Convert raw entries (which may contain ORM objects) to response models
    result: list[CalendarEntry] = []
    for entry in entries:
        video_responses: list[VideoSummaryResponse] = []
        for item in entry["videos"]:
            try:
                video_responses.append(VideoSummaryResponse.model_validate(item))
            except Exception:
                # Publish jobs don't conform to VideoSummaryResponse;
                # create a minimal representation
                video_responses.append(
                    VideoSummaryResponse(
                        id=str(item.id),
                        platform_video_id=item.platform_video_id or item.publish_id,
                        title=item.title,
                        status=item.status,
                        view_count=0,
                        like_count=0,
                        comment_count=0,
                        share_count=0,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )

        result.append(
            CalendarEntry(
                date=entry["date"],
                video_count=entry["video_count"],
                videos=video_responses,
            )
        )

    return result
