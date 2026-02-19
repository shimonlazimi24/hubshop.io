import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from backend.auth.jwt import create_access_token, create_refresh_token, decode_token
from backend.auth.passwords import hash_password, verify_password
from backend.db.models.organization import Membership, Organization, Role, Workspace
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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
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

    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
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
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
    )
