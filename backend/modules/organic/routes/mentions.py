import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.organic.services.mentions_service import MentionsService

router = APIRouter()


class ReplyToMentionRequest(BaseModel):
    connected_account_id: uuid.UUID
    comment_id: str
    text: str


class EnableBrandHashtagRequest(BaseModel):
    connected_account_id: uuid.UUID
    hashtag: str


@router.get("/mentions/posts/top")
async def get_top_mentions(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.get_top_mentions(workspace_id, connected_account_id)


@router.get("/mentions/posts/detail")
async def get_mention_detail(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    post_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.get_mention_detail(
        workspace_id, connected_account_id, post_id=post_id
    )


@router.get("/mentions/keywords/frequent")
async def get_frequent_keywords(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.get_frequent_keywords(workspace_id, connected_account_id)


@router.get("/mentions/hashtags/frequent")
async def get_frequent_hashtags(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.get_frequent_hashtags(workspace_id, connected_account_id)


@router.get("/mentions/comments/top")
async def get_top_comment_mentions(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.get_top_comment_mentions(workspace_id, connected_account_id)


@router.post("/mentions/comments/reply")
async def reply_to_mention(
    workspace_id: uuid.UUID,
    body: ReplyToMentionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.reply_to_mention(
        workspace_id,
        body.connected_account_id,
        comment_id=body.comment_id,
        text=body.text,
    )


@router.post("/mentions/brand_hashtag/enable")
async def enable_brand_hashtag(
    workspace_id: uuid.UUID,
    body: EnableBrandHashtagRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.enable_brand_hashtag(
        workspace_id,
        body.connected_account_id,
        hashtag=body.hashtag,
    )


@router.get("/mentions/brand_hashtag/enabled")
async def list_enabled_hashtags(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = MentionsService(db)
    return await service.list_enabled_hashtags(workspace_id, connected_account_id)
