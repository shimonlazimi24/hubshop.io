import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.comment_service import CommentService

router = APIRouter()


class ReplyCommentRequest(BaseModel):
    ad_account_id: str
    text: str


class CommentActionRequest(BaseModel):
    ad_account_id: str


@router.get("/comments")
async def list_comments(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    ad_id: str,
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

    service = CommentService(db)
    return await service.list_comments(
        workspace_id, ad_account, ad_id=ad_id, page=page, page_size=page_size
    )


@router.post("/comments/{comment_id}/reply")
async def reply_to_comment(
    workspace_id: uuid.UUID,
    comment_id: str,
    body: ReplyCommentRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = CommentService(db)
    return await service.reply_to_comment(
        workspace_id, ad_account, comment_id=comment_id, text=body.text
    )


@router.post("/comments/{comment_id}/hide")
async def hide_comment(
    workspace_id: uuid.UUID,
    comment_id: str,
    body: CommentActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = CommentService(db)
    return await service.hide_comment(workspace_id, ad_account, comment_id=comment_id)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    workspace_id: uuid.UUID,
    comment_id: str,
    body: CommentActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = CommentService(db)
    return await service.delete_comment(workspace_id, ad_account, comment_id=comment_id)
