import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.content.schemas import CommentResponse, ReplyToCommentRequest
from backend.modules.content.services.comment_service import CommentService
from backend.modules.content.services.video_service import VideoService

router = APIRouter()


@router.get(
    "/videos/{video_id}/comments",
    response_model=PaginatedResponse[CommentResponse],
)
async def list_comments(
    workspace_id: uuid.UUID,
    video_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CommentResponse]:
    service = CommentService(db)
    result = await service.list_comments(
        workspace_id, video_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[CommentResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/videos/{video_id}/comments/sync")
async def sync_comments(
    workspace_id: uuid.UUID,
    video_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    video_service = VideoService(db)
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    service = CommentService(db)
    count = await service.sync_comments(workspace_id, video)
    return {"synced": count}


@router.post("/videos/{video_id}/comments/{comment_id}/reply")
async def reply_to_comment(
    workspace_id: uuid.UUID,
    video_id: uuid.UUID,
    comment_id: str,
    body: ReplyToCommentRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    video_service = VideoService(db)
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    service = CommentService(db)
    return await service.reply_to_comment(workspace_id, video, comment_id, body.text)


@router.delete("/videos/{video_id}/comments/{comment_id}")
async def delete_comment(
    workspace_id: uuid.UUID,
    video_id: uuid.UUID,
    comment_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    video_service = VideoService(db)
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    service = CommentService(db)
    await service.delete_comment(workspace_id, video, comment_id)
    return {"deleted": True}
