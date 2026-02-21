import uuid
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select

from backend.config import settings
from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.dependencies import CurrentUser, DBSession
from backend.utils.crypto import encrypt_token

# Full production scopes for each platform connection
DEVELOPER_SCOPES = (
    "user.info.basic,"
    "user.info.profile,"
    "user.info.stats,"
    "video.list,"
    "video.publish,"
    "video.upload,"
    "comment.list,"
    "comment.list.manage"
)

router = APIRouter(prefix="/connect", tags=["connect"])


class ConnectedAccountResponse(BaseModel):
    id: uuid.UUID
    platform: str
    platform_account_id: str
    platform_account_name: str | None
    status: str
    identity_group_id: uuid.UUID | None


class AuthorizeResponse(BaseModel):
    authorize_url: str


# ─── Shop OAuth ──────────────────────────────────────────────────────────────


@router.get("/shop/authorize", response_model=AuthorizeResponse)
async def shop_authorize(workspace_id: uuid.UUID, current_user: CurrentUser) -> AuthorizeResponse:
    """Generate TikTok Shop OAuth authorization URL."""
    state = f"{workspace_id}:{current_user.id}"
    params = {
        "service_id": settings.tiktok_shop_app_key,
        "state": state,
    }
    url = f"https://services.tiktokshops.us/open/authorize?{urlencode(params)}"
    return AuthorizeResponse(authorize_url=url)


@router.get("/shop/callback")
async def shop_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: DBSession = ...,  # type: ignore[assignment]
) -> ConnectedAccountResponse:
    """Handle TikTok Shop OAuth callback. Exchange code for tokens."""
    parts = state.split(":")
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    workspace_id = uuid.UUID(parts[0])

    # Exchange authorization code for access token
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://auth.tiktok-shops.com/api/v2/token/get",
            params={
                "app_key": settings.tiktok_shop_app_key,
                "app_secret": settings.tiktok_shop_app_secret,
                "auth_code": code,
                "grant_type": "authorized_code",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if data.get("code") != 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TikTok Shop token exchange failed: {data.get('message')}",
        )

    token_data = data["data"]
    seller_id = str(token_data.get("seller_id", ""))

    account = ConnectedAccount(
        workspace_id=workspace_id,
        platform=Platform.SHOP,
        platform_account_id=seller_id,
        platform_account_name=token_data.get("seller_name"),
        status=AccountStatus.ACTIVE,
        metadata_json={"shop_ciphers": token_data.get("shop_cipher_list", [])},
    )
    db.add(account)
    await db.flush()

    token_vault = TokenVault(
        connected_account_id=account.id,
        encrypted_access_token=encrypt_token(token_data["access_token"]),
        encrypted_refresh_token=encrypt_token(token_data["refresh_token"]),
        access_token_expires_at=str(token_data.get("access_token_expire_in", "")),
        refresh_token_expires_at=str(token_data.get("refresh_token_expire_in", "")),
    )
    db.add(token_vault)

    return ConnectedAccountResponse(
        id=account.id,
        platform=account.platform.value,
        platform_account_id=account.platform_account_id,
        platform_account_name=account.platform_account_name,
        status=account.status.value,
        identity_group_id=account.identity_group_id,
    )


# ─── Developer OAuth ────────────────────────────────────────────────────────


@router.get("/developer/authorize", response_model=AuthorizeResponse)
async def developer_authorize(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
) -> AuthorizeResponse:
    """Generate TikTok Developer OAuth authorization URL."""
    state = f"{workspace_id}:{current_user.id}"
    params = {
        "client_key": settings.tiktok_developer_client_key,
        "response_type": "code",
        "scope": DEVELOPER_SCOPES,
        "redirect_uri": f"{settings.backend_url}/api/connect/developer/callback",
        "state": state,
    }
    url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(params)}"
    return AuthorizeResponse(authorize_url=url)


@router.get("/developer/callback")
async def developer_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: DBSession = ...,  # type: ignore[assignment]
) -> ConnectedAccountResponse:
    """Handle TikTok Developer OAuth callback."""
    parts = state.split(":")
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    workspace_id = uuid.UUID(parts[0])

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": settings.tiktok_developer_client_key,
                "client_secret": settings.tiktok_developer_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.backend_url}/api/connect/developer/callback",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if "access_token" not in data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TikTok Developer token exchange failed: {data.get('error_description')}",
        )

    open_id = data.get("open_id", "")

    account = ConnectedAccount(
        workspace_id=workspace_id,
        platform=Platform.DEVELOPER,
        platform_account_id=open_id,
        status=AccountStatus.ACTIVE,
        metadata_json={"scope": data.get("scope", "")},
    )
    db.add(account)
    await db.flush()

    token_vault = TokenVault(
        connected_account_id=account.id,
        encrypted_access_token=encrypt_token(data["access_token"]),
        encrypted_refresh_token=encrypt_token(data.get("refresh_token", "")),
        access_token_expires_at=str(data.get("expires_in", "")),
        refresh_token_expires_at=str(data.get("refresh_expires_in", "")),
        scopes=data.get("scope", ""),
    )
    db.add(token_vault)

    return ConnectedAccountResponse(
        id=account.id,
        platform=account.platform.value,
        platform_account_id=account.platform_account_id,
        platform_account_name=account.platform_account_name,
        status=account.status.value,
        identity_group_id=account.identity_group_id,
    )


# ─── Marketing OAuth ────────────────────────────────────────────────────────


@router.get("/marketing/authorize", response_model=AuthorizeResponse)
async def marketing_authorize(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
) -> AuthorizeResponse:
    """Generate TikTok Marketing OAuth authorization URL."""
    state = f"{workspace_id}:{current_user.id}"
    params = {
        "app_id": settings.tiktok_marketing_app_id,
        "redirect_uri": f"{settings.backend_url}/api/connect/marketing/callback",
        "state": state,
    }
    url = f"https://business-api.tiktok.com/portal/auth?{urlencode(params)}"
    return AuthorizeResponse(authorize_url=url)


@router.get("/marketing/callback")
async def marketing_callback(
    auth_code: str = Query(...),
    state: str = Query(...),
    db: DBSession = ...,  # type: ignore[assignment]
) -> ConnectedAccountResponse:
    """Handle TikTok Marketing OAuth callback."""
    parts = state.split(":")
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    workspace_id = uuid.UUID(parts[0])

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/",
            json={
                "app_id": settings.tiktok_marketing_app_id,
                "secret": settings.tiktok_marketing_app_secret,
                "auth_code": auth_code,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if data.get("code") != 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TikTok Marketing token exchange failed: {data.get('message')}",
        )

    token_data = data["data"]
    advertiser_ids = token_data.get("advertiser_ids", [])
    primary_id = str(advertiser_ids[0]) if advertiser_ids else ""

    account = ConnectedAccount(
        workspace_id=workspace_id,
        platform=Platform.MARKETING,
        platform_account_id=primary_id,
        status=AccountStatus.ACTIVE,
        metadata_json={"advertiser_ids": advertiser_ids},
    )
    db.add(account)
    await db.flush()

    token_vault = TokenVault(
        connected_account_id=account.id,
        encrypted_access_token=encrypt_token(token_data["access_token"]),
    )
    db.add(token_vault)

    return ConnectedAccountResponse(
        id=account.id,
        platform=account.platform.value,
        platform_account_id=account.platform_account_id,
        platform_account_name=account.platform_account_name,
        status=account.status.value,
        identity_group_id=account.identity_group_id,
    )


# ─── Account Listing ────────────────────────────────────────────────────────


@router.get("/accounts", response_model=list[ConnectedAccountResponse])
async def list_connected_accounts(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ConnectedAccountResponse]:
    """List all connected TikTok accounts for a workspace."""
    result = await db.execute(
        select(ConnectedAccount).where(ConnectedAccount.workspace_id == workspace_id)
    )
    accounts = result.scalars().all()
    return [
        ConnectedAccountResponse(
            id=a.id,
            platform=a.platform.value,
            platform_account_id=a.platform_account_id,
            platform_account_name=a.platform_account_name,
            status=a.status.value,
            identity_group_id=a.identity_group_id,
        )
        for a in accounts
    ]
