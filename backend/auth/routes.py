import logging
import uuid
from datetime import UTC, datetime

import httpx
import redis.asyncio as redis
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from backend.auth.jwt import create_access_token, create_refresh_token, decode_token
from backend.auth.passwords import (
    hash_password_async,
    validate_password,
    verify_password_async,
)
from backend.auth.social import SocialAuthService
from backend.auth.token_blacklist import blacklist_token, is_token_blacklisted
from backend.config import settings
from backend.db.models.organization import Membership, Organization, Role, Workspace
from backend.db.models.social_identity import SocialProvider
from backend.db.models.user import User
from backend.dependencies import CurrentUser, DBSession

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None

_OAUTH_STATE_TTL = 600  # 10 minutes

# Login rate limiting
_LOGIN_MAX_ATTEMPTS = 5
_LOGIN_WINDOW_SECONDS = 300  # 5 minutes


async def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def _check_login_rate_limit(email: str) -> None:
    """Enforce per-email rate limit on login attempts.

    Raises HTTP 429 if the limit is exceeded.
    """
    try:
        r = await _get_redis()
        key = f"login_rate_limit:{email.lower()}"
        attempts = await r.incr(key)
        if attempts == 1:
            await r.expire(key, _LOGIN_WINDOW_SECONDS)
        if attempts > _LOGIN_MAX_ATTEMPTS:
            ttl = await r.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Try again in {max(ttl, 1)} seconds.",
            )
    except HTTPException:
        raise
    except Exception:
        # If Redis is unavailable, log and allow the request (fail-open for auth)
        logger.warning("Login rate limiter unavailable — skipping check")


router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    workspace_id: uuid.UUID | None = None


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(body: RegisterRequest, db: DBSession) -> TokenResponse:
    """Register a new user, create their organization and default workspace."""
    validate_password(body.password)

    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=body.email,
        hashed_password=await hash_password_async(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.flush()

    slug = body.organization_name.lower().replace(" ", "-")[:50]
    org = Organization(name=body.organization_name, slug=slug)
    db.add(org)
    await db.flush()

    workspace = Workspace(
        name="Default",
        slug="default",
        organization_id=org.id,
    )
    db.add(workspace)
    await db.flush()

    membership = Membership(
        user_id=user.id,
        organization_id=org.id,
        workspace_id=workspace.id,
        role=Role.OWNER,
    )
    db.add(membership)

    return TokenResponse(
        access_token=create_access_token(user.id, org.id, Role.OWNER.value),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DBSession) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    await _check_login_rate_limit(body.email)

    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses social login. Please sign in with TikTok or Google.",
        )
    if not await verify_password_async(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Get the user's first org membership for the default token
    membership_result = await db.execute(
        select(Membership).where(Membership.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    org_id = membership.organization_id if membership else None
    role = membership.role.value if membership else None

    return TokenResponse(
        access_token=create_access_token(user.id, org_id, role),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request) -> dict:
    """Logout by blacklisting the current access token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = auth_header.removeprefix("Bearer ")

    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing jti claim",
        )

    # Calculate remaining TTL in seconds
    exp = payload.get("exp", 0)
    remaining = int(exp - datetime.now(UTC).timestamp())
    if remaining > 0:
        await blacklist_token(jti, remaining)

    return {"detail": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(body: RefreshRequest, db: DBSession) -> TokenResponse:
    """Refresh access token using a valid refresh token."""
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = uuid.UUID(payload["sub"])
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    # Check if this refresh token has been blacklisted (rotation)
    old_jti = payload.get("jti")
    if old_jti and await is_token_blacklisted(old_jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    # Blacklist the old refresh token so it cannot be reused
    if old_jti:
        exp = payload.get("exp", 0)
        remaining = int(exp - datetime.now(UTC).timestamp())
        if remaining > 0:
            await blacklist_token(old_jti, remaining)

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    membership_result = await db.execute(
        select(Membership).where(Membership.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            membership.organization_id if membership else None,
            membership.role.value if membership else None,
        ),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """Get the current authenticated user."""
    workspace_id = None
    if current_user.memberships:
        workspace_id = current_user.memberships[0].workspace_id
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        workspace_id=workspace_id,
    )


# ---------------------------------------------------------------------------
# Social Login
# ---------------------------------------------------------------------------


class SocialLoginResponse(BaseModel):
    authorize_url: str


@router.get("/tiktok/login", response_model=SocialLoginResponse)
async def tiktok_login() -> SocialLoginResponse:
    """Return the TikTok OAuth authorize URL."""
    state = uuid.uuid4().hex
    r = await _get_redis()
    await r.set(f"oauth_state:{state}", "1", ex=_OAUTH_STATE_TTL)
    url = SocialAuthService.build_tiktok_login_url(state)
    return SocialLoginResponse(authorize_url=url)


@router.get("/tiktok/callback", response_model=TokenResponse)
async def tiktok_callback(
    db: DBSession,
    code: str = Query(...),
    state: str = Query(""),
) -> TokenResponse:
    """Exchange TikTok auth code for JWT tokens."""
    r = await _get_redis()
    state_key = f"oauth_state:{state}"
    if not state or not await r.get(state_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state",
        )
    await r.delete(state_key)

    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": settings.tiktok_developer_client_key,
                "client_secret": settings.tiktok_developer_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.tiktok_login_redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to exchange TikTok auth code",
            )

        token_data = token_resp.json()
        access_token = token_data.get("access_token") or token_data.get("data", {}).get(
            "access_token"
        )
        open_id = token_data.get("open_id") or token_data.get("data", {}).get("open_id")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="TikTok did not return an access token",
            )

        # Fetch user info
        user_resp = await client.get(
            "https://open.tiktokapis.com/v2/user/info/",
            params={"fields": "open_id,display_name,avatar_url"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_resp.json().get("data", {}).get("user", {})

    provider_user_id = open_id or user_data.get("open_id", "")
    display_name = user_data.get("display_name")
    avatar_url = user_data.get("avatar_url")

    svc = SocialAuthService(db)
    user, _ = await svc.get_or_create_user(
        provider=SocialProvider.TIKTOK,
        provider_user_id=provider_user_id,
        display_name=display_name,
        avatar_url=avatar_url,
    )

    membership_result = await db.execute(
        select(Membership).where(Membership.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    org_id = membership.organization_id if membership else None
    role = membership.role.value if membership else None

    return TokenResponse(
        access_token=create_access_token(user.id, org_id, role),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/google/login", response_model=SocialLoginResponse)
async def google_login() -> SocialLoginResponse:
    """Return the Google OAuth authorize URL."""
    state = uuid.uuid4().hex
    r = await _get_redis()
    await r.set(f"oauth_state:{state}", "1", ex=_OAUTH_STATE_TTL)
    url = SocialAuthService.build_google_login_url(state)
    return SocialLoginResponse(authorize_url=url)


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    db: DBSession,
    code: str = Query(...),
    state: str = Query(""),
) -> TokenResponse:
    """Exchange Google auth code for JWT tokens."""
    r = await _get_redis()
    state_key = f"oauth_state:{state}"
    if not state or not await r.get(state_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state",
        )
    await r.delete(state_key)

    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to exchange Google auth code",
            )

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Google did not return an access token",
            )

        # Fetch user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch Google user info",
            )
        user_data = user_resp.json()

    provider_user_id = user_data.get("id", "")
    email = user_data.get("email")
    display_name = user_data.get("name")
    avatar_url = user_data.get("picture")

    svc = SocialAuthService(db)
    user, _ = await svc.get_or_create_user(
        provider=SocialProvider.GOOGLE,
        provider_user_id=provider_user_id,
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
    )

    membership_result = await db.execute(
        select(Membership).where(Membership.user_id == user.id).limit(1)
    )
    membership = membership_result.scalar_one_or_none()

    org_id = membership.organization_id if membership else None
    role = membership.role.value if membership else None

    return TokenResponse(
        access_token=create_access_token(user.id, org_id, role),
        refresh_token=create_refresh_token(user.id),
    )
