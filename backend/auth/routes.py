import uuid

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from backend.auth.jwt import create_access_token, create_refresh_token, decode_token
from backend.auth.passwords import hash_password, verify_password
from backend.auth.social import SocialAuthService
from backend.config import settings
from backend.db.models.organization import Membership, Organization, Role, Workspace
from backend.db.models.social_identity import SocialProvider
from backend.db.models.user import User
from backend.dependencies import CurrentUser, DBSession

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
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
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
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
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
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

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
    url = SocialAuthService.build_tiktok_login_url(state)
    return SocialLoginResponse(authorize_url=url)


@router.get("/tiktok/callback", response_model=TokenResponse)
async def tiktok_callback(
    db: DBSession,
    code: str = Query(...),
    state: str = Query(""),
) -> TokenResponse:
    """Exchange TikTok auth code for JWT tokens."""
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
    url = SocialAuthService.build_google_login_url(state)
    return SocialLoginResponse(authorize_url=url)


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    db: DBSession,
    code: str = Query(...),
    state: str = Query(""),
) -> TokenResponse:
    """Exchange Google auth code for JWT tokens."""
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
