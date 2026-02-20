"""Tests for intelligence sync Celery workers."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSyncTrends:
    @pytest.mark.asyncio
    async def test_skips_when_no_credentials(self) -> None:
        """Should skip sync when research API credentials aren't configured."""
        mock_settings = MagicMock()
        mock_settings.tiktok_research_client_key = ""
        mock_settings.tiktok_research_client_secret = ""

        with patch("backend.workers.intelligence_sync.settings", mock_settings):
            from backend.workers.intelligence_sync import _sync_trends

            await _sync_trends()

    @pytest.mark.asyncio
    async def test_syncs_trends_for_all_workspaces(self) -> None:
        """Should iterate all workspaces and call TrendService.sync_trends."""
        ws1 = SimpleNamespace(id=uuid.uuid4())
        ws2 = SimpleNamespace(id=uuid.uuid4())

        mock_settings = MagicMock()
        mock_settings.tiktok_research_client_key = "test_key"
        mock_settings.tiktok_research_client_secret = "test_secret"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [ws1, ws2]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_trend_service = MagicMock()
        mock_trend_service.sync_trends = AsyncMock()

        mock_research_client = MagicMock()
        mock_research_client.close = AsyncMock()

        with (
            patch("backend.workers.intelligence_sync.settings", mock_settings),
            patch(
                "backend.workers.intelligence_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.intelligence_sync.TikTokResearchClient",
                return_value=mock_research_client,
            ),
            patch(
                "backend.workers.intelligence_sync.TrendService",
                return_value=mock_trend_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.intelligence_sync import _sync_trends

            await _sync_trends()

        mock_research_client.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handles_workspace_sync_failure(self) -> None:
        """Should rollback and continue if one workspace fails."""
        ws1 = SimpleNamespace(id=uuid.uuid4())

        mock_settings = MagicMock()
        mock_settings.tiktok_research_client_key = "test_key"
        mock_settings.tiktok_research_client_secret = "test_secret"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [ws1]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_research_client = MagicMock()
        mock_research_client.close = AsyncMock()

        mock_trend_service = MagicMock()
        mock_trend_service.sync_trends = AsyncMock(
            side_effect=RuntimeError("API error")
        )

        with (
            patch("backend.workers.intelligence_sync.settings", mock_settings),
            patch(
                "backend.workers.intelligence_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.intelligence_sync.TikTokResearchClient",
                return_value=mock_research_client,
            ),
            patch(
                "backend.workers.intelligence_sync.TrendService",
                return_value=mock_trend_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.intelligence_sync import _sync_trends

            await _sync_trends()

        mock_session.rollback.assert_awaited()
        mock_research_client.close.assert_awaited_once()


class TestSyncCompetitorContent:
    @pytest.mark.asyncio
    async def test_skips_when_no_credentials(self) -> None:
        """Should skip sync when research API credentials aren't configured."""
        mock_settings = MagicMock()
        mock_settings.tiktok_research_client_key = ""
        mock_settings.tiktok_research_client_secret = ""

        with patch("backend.workers.intelligence_sync.settings", mock_settings):
            from backend.workers.intelligence_sync import _sync_competitor_content

            await _sync_competitor_content()

    @pytest.mark.asyncio
    async def test_syncs_competitors_for_all_workspaces(self) -> None:
        """Should iterate all workspaces and call CompetitorService."""
        ws1 = SimpleNamespace(id=uuid.uuid4())

        mock_settings = MagicMock()
        mock_settings.tiktok_research_client_key = "test_key"
        mock_settings.tiktok_research_client_secret = "test_secret"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [ws1]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_competitor_service = MagicMock()
        mock_competitor_service.sync_all_competitors = AsyncMock()

        mock_research_client = MagicMock()
        mock_research_client.close = AsyncMock()

        with (
            patch("backend.workers.intelligence_sync.settings", mock_settings),
            patch(
                "backend.workers.intelligence_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.intelligence_sync.TikTokResearchClient",
                return_value=mock_research_client,
            ),
            patch(
                "backend.workers.intelligence_sync.CompetitorService",
                return_value=mock_competitor_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.intelligence_sync import _sync_competitor_content

            await _sync_competitor_content()

        mock_research_client.close.assert_awaited_once()


class TestCeleryTaskRegistration:
    def test_sync_trends_task_exists(self) -> None:
        """sync_trends should be a registered Celery task."""
        from backend.workers.intelligence_sync import sync_trends

        assert sync_trends.name == "backend.workers.intelligence_sync.sync_trends"

    def test_sync_competitor_content_task_exists(self) -> None:
        """sync_competitor_content should be a registered Celery task."""
        from backend.workers.intelligence_sync import sync_competitor_content

        assert (
            sync_competitor_content.name
            == "backend.workers.intelligence_sync.sync_competitor_content"
        )
