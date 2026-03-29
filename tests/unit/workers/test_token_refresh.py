"""Tests for the token_refresh Celery worker (backend/workers/token_refresh.py)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.platform import AccountStatus, Platform


@pytest.mark.unit
class TestRefreshDeveloperToken:
    """Tests for _refresh_developer_token HTTP call."""

    async def test_successful_developer_token_refresh(self) -> None:
        """Should return new tokens on a 200 response with access_token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-dev-access-token",
            "refresh_token": "new-dev-refresh-token",
            "expires_in": 86400,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "backend.workers.token_refresh.httpx.AsyncClient", return_value=mock_client
        ):
            from backend.workers.token_refresh import _refresh_developer_token

            result = await _refresh_developer_token(uuid.uuid4(), "old-refresh-token")

        assert result is not None
        assert result["access_token"] == "new-dev-access-token"

    async def test_failed_developer_token_refresh_returns_none(self) -> None:
        """Should return None on a non-200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "backend.workers.token_refresh.httpx.AsyncClient", return_value=mock_client
        ):
            from backend.workers.token_refresh import _refresh_developer_token

            result = await _refresh_developer_token(uuid.uuid4(), "bad-refresh-token")

        assert result is None

    async def test_developer_refresh_missing_access_token_returns_none(self) -> None:
        """Should return None when response is 200 but lacks access_token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "invalid_grant"}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "backend.workers.token_refresh.httpx.AsyncClient", return_value=mock_client
        ):
            from backend.workers.token_refresh import _refresh_developer_token

            result = await _refresh_developer_token(uuid.uuid4(), "some-token")

        assert result is None


@pytest.mark.unit
class TestRefreshShopToken:
    """Tests for _refresh_shop_token HTTP call."""

    async def test_successful_shop_token_refresh(self) -> None:
        """Should return token data on a successful response (code=0)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "access_token": "new-shop-access",
                "refresh_token": "new-shop-refresh",
                "access_token_expire_in": 604800,
            },
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "backend.workers.token_refresh.httpx.AsyncClient", return_value=mock_client
        ):
            from backend.workers.token_refresh import _refresh_shop_token

            result = await _refresh_shop_token(uuid.uuid4(), "old-refresh")

        assert result is not None
        assert result["access_token"] == "new-shop-access"

    async def test_failed_shop_token_refresh_returns_none(self) -> None:
        """Should return None on non-200 or error code response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 1, "message": "invalid token"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "backend.workers.token_refresh.httpx.AsyncClient", return_value=mock_client
        ):
            from backend.workers.token_refresh import _refresh_shop_token

            result = await _refresh_shop_token(uuid.uuid4(), "expired-token")

        assert result is None


@pytest.mark.unit
class TestDoRefreshDeveloperTokens:
    """Tests for the _do_refresh_developer_tokens orchestrator."""

    async def test_refreshes_active_developer_accounts(self) -> None:
        """Should refresh tokens for all active developer accounts."""
        account = MagicMock()
        account.id = uuid.uuid4()
        account.platform = Platform.DEVELOPER
        account.status = AccountStatus.ACTIVE

        vault = MagicMock()
        vault.encrypted_refresh_token = "encrypted-refresh"
        vault.encrypted_access_token = "encrypted-access"

        mock_session = AsyncMock()
        # First call returns accounts, second call returns vault
        mock_accounts_result = MagicMock()
        mock_accounts_result.scalars.return_value.all.return_value = [account]
        mock_vault_result = MagicMock()
        mock_vault_result.scalar_one_or_none.return_value = vault

        mock_session.execute = AsyncMock(
            side_effect=[mock_accounts_result, mock_vault_result]
        )
        mock_session.commit = AsyncMock()

        with (
            patch(
                "backend.workers.token_refresh.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.token_refresh.decrypt_token",
                return_value="decrypted-refresh-token",
            ),
            patch(
                "backend.workers.token_refresh._refresh_developer_token",
                new_callable=AsyncMock,
                return_value={
                    "access_token": "new-access",
                    "refresh_token": "new-refresh",
                    "expires_in": 86400,
                },
            ),
            patch(
                "backend.workers.token_refresh.encrypt_token",
                return_value="encrypted-new",
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.token_refresh import _do_refresh_developer_tokens

            await _do_refresh_developer_tokens()

        mock_session.commit.assert_awaited_once()

    async def test_marks_account_as_error_on_refresh_failure(self) -> None:
        """Should set account status to ERROR when token refresh fails."""
        account = MagicMock()
        account.id = uuid.uuid4()
        account.status = AccountStatus.ACTIVE

        vault = MagicMock()
        vault.encrypted_refresh_token = "encrypted-refresh"

        mock_session = AsyncMock()
        mock_accounts_result = MagicMock()
        mock_accounts_result.scalars.return_value.all.return_value = [account]
        mock_vault_result = MagicMock()
        mock_vault_result.scalar_one_or_none.return_value = vault

        mock_session.execute = AsyncMock(
            side_effect=[mock_accounts_result, mock_vault_result]
        )
        mock_session.commit = AsyncMock()

        with (
            patch(
                "backend.workers.token_refresh.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.token_refresh.decrypt_token",
                return_value="decrypted-refresh",
            ),
            patch(
                "backend.workers.token_refresh._refresh_developer_token",
                new_callable=AsyncMock,
                return_value=None,  # Refresh failed
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.token_refresh import _do_refresh_developer_tokens

            await _do_refresh_developer_tokens()

        assert account.status == AccountStatus.ERROR

    async def test_skips_account_without_vault(self) -> None:
        """Should skip accounts without a token vault entry."""
        account = MagicMock()
        account.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_accounts_result = MagicMock()
        mock_accounts_result.scalars.return_value.all.return_value = [account]
        mock_vault_result = MagicMock()
        mock_vault_result.scalar_one_or_none.return_value = None  # No vault

        mock_session.execute = AsyncMock(
            side_effect=[mock_accounts_result, mock_vault_result]
        )
        mock_session.commit = AsyncMock()

        with (
            patch(
                "backend.workers.token_refresh.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.token_refresh._refresh_developer_token",
                new_callable=AsyncMock,
            ) as mock_refresh,
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.token_refresh import _do_refresh_developer_tokens

            await _do_refresh_developer_tokens()

        mock_refresh.assert_not_awaited()


@pytest.mark.unit
class TestDoCheckMarketingTokens:
    """Tests for _do_check_marketing_tokens health check."""

    async def test_marks_account_error_on_invalid_token(self) -> None:
        """Should mark account as ERROR when marketing API returns failure."""
        account = MagicMock()
        account.id = uuid.uuid4()
        account.status = AccountStatus.ACTIVE

        vault = MagicMock()
        vault.encrypted_access_token = "encrypted-access"

        mock_session = AsyncMock()
        mock_accounts_result = MagicMock()
        mock_accounts_result.scalars.return_value.all.return_value = [account]
        mock_vault_result = MagicMock()
        mock_vault_result.scalar_one_or_none.return_value = vault

        mock_session.execute = AsyncMock(
            side_effect=[mock_accounts_result, mock_vault_result]
        )
        mock_session.commit = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 40100, "message": "unauthorized"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "backend.workers.token_refresh.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.token_refresh.decrypt_token",
                return_value="decrypted-access",
            ),
            patch(
                "backend.workers.token_refresh.httpx.AsyncClient",
                return_value=mock_client,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.token_refresh import _do_check_marketing_tokens

            await _do_check_marketing_tokens()

        assert account.status == AccountStatus.ERROR

    async def test_healthy_marketing_token_not_marked_error(self) -> None:
        """Should leave account status unchanged when token is valid."""
        account = MagicMock()
        account.id = uuid.uuid4()
        account.status = AccountStatus.ACTIVE

        vault = MagicMock()
        vault.encrypted_access_token = "encrypted-access"

        mock_session = AsyncMock()
        mock_accounts_result = MagicMock()
        mock_accounts_result.scalars.return_value.all.return_value = [account]
        mock_vault_result = MagicMock()
        mock_vault_result.scalar_one_or_none.return_value = vault

        mock_session.execute = AsyncMock(
            side_effect=[mock_accounts_result, mock_vault_result]
        )
        mock_session.commit = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "data": {"display_name": "User"}}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "backend.workers.token_refresh.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.token_refresh.decrypt_token",
                return_value="valid-access",
            ),
            patch(
                "backend.workers.token_refresh.httpx.AsyncClient",
                return_value=mock_client,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.token_refresh import _do_check_marketing_tokens

            await _do_check_marketing_tokens()

        # Status should remain ACTIVE (not changed to ERROR)
        assert account.status == AccountStatus.ACTIVE


@pytest.mark.unit
class TestCeleryTaskRegistration:
    """Verify Celery tasks are properly registered."""

    def test_refresh_developer_tokens_task_name(self) -> None:
        from backend.workers.token_refresh import refresh_developer_tokens

        assert (
            refresh_developer_tokens.name
            == "backend.workers.token_refresh.refresh_developer_tokens"
        )

    def test_refresh_shop_tokens_task_name(self) -> None:
        from backend.workers.token_refresh import refresh_shop_tokens

        assert (
            refresh_shop_tokens.name
            == "backend.workers.token_refresh.refresh_shop_tokens"
        )

    def test_check_marketing_tokens_task_name(self) -> None:
        from backend.workers.token_refresh import check_marketing_tokens

        assert (
            check_marketing_tokens.name
            == "backend.workers.token_refresh.check_marketing_tokens"
        )

    def test_tasks_have_retry_config(self) -> None:
        from backend.workers.token_refresh import refresh_developer_tokens

        assert refresh_developer_tokens.max_retries == 3
