"""Tests for FastAPI dependency injection functions (backend/dependencies.py)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from backend.dependencies import get_current_user, get_workspace_id


@pytest.mark.unit
class TestGetWorkspaceId:
    """Tests for the get_workspace_id dependency."""

    async def test_valid_workspace_with_membership(self) -> None:
        """Valid workspace_id header with an existing membership returns UUID."""
        user = MagicMock()
        user.id = uuid.uuid4()

        workspace_id = uuid.uuid4()
        workspace = MagicMock()
        workspace.id = workspace_id
        workspace.organization_id = uuid.uuid4()

        membership = MagicMock()
        membership.workspace_id = workspace_id

        mock_db = AsyncMock()
        # First call: workspace lookup, second call: membership lookup
        ws_result = MagicMock()
        ws_result.scalar_one_or_none.return_value = workspace
        mem_result = MagicMock()
        mem_result.scalar_one_or_none.return_value = membership
        mock_db.execute = AsyncMock(side_effect=[ws_result, mem_result])

        result = await get_workspace_id(
            current_user=user,
            db=mock_db,
            x_workspace_id=str(workspace_id),
        )

        assert result == workspace_id

    async def test_workspace_not_found_raises_404(self) -> None:
        """Workspace that doesn't exist raises 404."""
        user = MagicMock()
        user.id = uuid.uuid4()

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await get_workspace_id(
                current_user=user,
                db=mock_db,
                x_workspace_id=str(uuid.uuid4()),
            )

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    async def test_valid_workspace_no_membership_raises_403(self) -> None:
        """Valid workspace_id with no membership raises 403."""
        user = MagicMock()
        user.id = uuid.uuid4()

        workspace = MagicMock()
        workspace.id = uuid.uuid4()
        workspace.organization_id = uuid.uuid4()

        mock_db = AsyncMock()
        ws_result = MagicMock()
        ws_result.scalar_one_or_none.return_value = workspace
        mem_result = MagicMock()
        mem_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(side_effect=[ws_result, mem_result])

        with pytest.raises(HTTPException) as exc_info:
            await get_workspace_id(
                current_user=user,
                db=mock_db,
                x_workspace_id=str(uuid.uuid4()),
            )

        assert exc_info.value.status_code == 403
        assert "Not authorized" in exc_info.value.detail

    async def test_invalid_uuid_raises_400(self) -> None:
        """Invalid UUID string in X-Workspace-Id header raises 400."""
        user = MagicMock()
        user.id = uuid.uuid4()
        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_workspace_id(
                current_user=user,
                db=mock_db,
                x_workspace_id="not-a-valid-uuid",
            )

        assert exc_info.value.status_code == 400
        assert "Invalid workspace ID format" in exc_info.value.detail

    async def test_missing_header_raises_400(self) -> None:
        """Missing X-Workspace-Id header raises 400."""
        user = MagicMock()
        user.id = uuid.uuid4()
        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_workspace_id(
                current_user=user,
                db=mock_db,
                x_workspace_id=None,
            )

        assert exc_info.value.status_code == 400
        assert "required" in exc_info.value.detail.lower()

    async def test_empty_string_header_raises_400(self) -> None:
        """Empty string in X-Workspace-Id header raises 400."""
        user = MagicMock()
        user.id = uuid.uuid4()
        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_workspace_id(
                current_user=user,
                db=mock_db,
                x_workspace_id="",
            )

        assert exc_info.value.status_code == 400

    async def test_org_wide_membership_grants_access(self) -> None:
        """Membership with workspace_id=NULL (org-wide) grants access."""
        user = MagicMock()
        user.id = uuid.uuid4()

        workspace_id = uuid.uuid4()
        workspace = MagicMock()
        workspace.id = workspace_id
        workspace.organization_id = uuid.uuid4()

        # Org-wide membership (workspace_id is None)
        membership = MagicMock()
        membership.workspace_id = None

        mock_db = AsyncMock()
        ws_result = MagicMock()
        ws_result.scalar_one_or_none.return_value = workspace
        mem_result = MagicMock()
        mem_result.scalar_one_or_none.return_value = membership
        mock_db.execute = AsyncMock(side_effect=[ws_result, mem_result])

        result = await get_workspace_id(
            current_user=user,
            db=mock_db,
            x_workspace_id=str(workspace_id),
        )

        assert result == workspace_id


@pytest.mark.unit
class TestGetCurrentUser:
    """Tests for the get_current_user dependency."""

    async def test_invalid_token_type_raises_401(self) -> None:
        """Token with type != 'access' should raise 401."""
        credentials = MagicMock()
        credentials.credentials = "some.jwt.token"
        mock_db = AsyncMock()

        with patch(
            "backend.dependencies.decode_token",
            return_value={"sub": str(uuid.uuid4()), "type": "refresh"},
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=credentials, db=mock_db)

            assert exc_info.value.status_code == 401
            assert "Invalid token type" in exc_info.value.detail

    async def test_blacklisted_token_raises_401(self) -> None:
        """Blacklisted token (revoked via logout) raises 401."""
        user_id = uuid.uuid4()
        credentials = MagicMock()
        credentials.credentials = "some.jwt.token"
        mock_db = AsyncMock()

        with (
            patch(
                "backend.dependencies.decode_token",
                return_value={
                    "sub": str(user_id),
                    "type": "access",
                    "jti": "revoked-jti",
                },
            ),
            patch(
                "backend.dependencies.is_token_blacklisted",
                return_value=True,
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=credentials, db=mock_db)

            assert exc_info.value.status_code == 401
            assert "revoked" in exc_info.value.detail.lower()

    async def test_user_not_found_raises_401(self) -> None:
        """Valid token but user does not exist in DB raises 401."""
        user_id = uuid.uuid4()
        credentials = MagicMock()
        credentials.credentials = "some.jwt.token"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with (
            patch(
                "backend.dependencies.decode_token",
                return_value={
                    "sub": str(user_id),
                    "type": "access",
                    "jti": "valid-jti",
                },
            ),
            patch(
                "backend.dependencies.is_token_blacklisted",
                return_value=False,
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=credentials, db=mock_db)

            assert exc_info.value.status_code == 401
            assert "User not found" in exc_info.value.detail

    async def test_valid_token_returns_user(self) -> None:
        """Valid token with active user returns user object."""
        user_id = uuid.uuid4()
        credentials = MagicMock()
        credentials.credentials = "some.jwt.token"

        mock_user = MagicMock()
        mock_user.id = user_id

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with (
            patch(
                "backend.dependencies.decode_token",
                return_value={
                    "sub": str(user_id),
                    "type": "access",
                    "jti": "valid-jti",
                },
            ),
            patch(
                "backend.dependencies.is_token_blacklisted",
                return_value=False,
            ),
        ):
            user = await get_current_user(credentials=credentials, db=mock_db)

        assert user.id == user_id
