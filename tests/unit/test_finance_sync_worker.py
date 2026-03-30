"""Tests for finance sync Celery workers — Phase B5."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSyncDailyStatements:
    @pytest.mark.asyncio
    async def test_syncs_all_shops(self) -> None:
        """Should call sync_settlements for every shop."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        shop1 = MagicMock(id=uuid.uuid4(), shop_name="Shop A")
        shop2 = MagicMock(id=uuid.uuid4(), shop_name="Shop B")

        shops_result = MagicMock()
        shops_result.scalars.return_value.all.return_value = [shop1, shop2]
        mock_session.execute = AsyncMock(return_value=shops_result)

        mock_finance_service = MagicMock()
        mock_finance_service.sync_settlements = AsyncMock(return_value=5)

        with (
            patch("backend.workers.finance_sync.async_session_factory") as mock_factory,
            patch(
                "backend.workers.finance_sync.FinanceService",
                return_value=mock_finance_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.finance_sync import _sync_daily_statements

            await _sync_daily_statements()

        assert mock_finance_service.sync_settlements.await_count == 2

    @pytest.mark.asyncio
    async def test_handles_shop_error_and_continues(self) -> None:
        """Should rollback on error but continue with next shop."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        shop1 = MagicMock(id=uuid.uuid4(), shop_name="Failing Shop")
        shop2 = MagicMock(id=uuid.uuid4(), shop_name="Good Shop")

        shops_result = MagicMock()
        shops_result.scalars.return_value.all.return_value = [shop1, shop2]
        mock_session.execute = AsyncMock(return_value=shops_result)

        mock_finance_service = MagicMock()
        mock_finance_service.sync_settlements = AsyncMock(
            side_effect=[RuntimeError("API error"), 3]
        )

        with (
            patch("backend.workers.finance_sync.async_session_factory") as mock_factory,
            patch(
                "backend.workers.finance_sync.FinanceService",
                return_value=mock_finance_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.finance_sync import _sync_daily_statements

            await _sync_daily_statements()

        mock_session.rollback.assert_awaited_once()
        assert mock_finance_service.sync_settlements.await_count == 2


class TestSyncUnsettledTransactions:
    @pytest.mark.asyncio
    async def test_syncs_all_shops(self) -> None:
        """Should call sync_transactions for every shop."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        shop1 = MagicMock(id=uuid.uuid4(), shop_name="Shop A")

        shops_result = MagicMock()
        shops_result.scalars.return_value.all.return_value = [shop1]
        mock_session.execute = AsyncMock(return_value=shops_result)

        mock_finance_service = MagicMock()
        mock_finance_service.sync_transactions = AsyncMock(return_value=10)

        with (
            patch("backend.workers.finance_sync.async_session_factory") as mock_factory,
            patch(
                "backend.workers.finance_sync.FinanceService",
                return_value=mock_finance_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.finance_sync import _sync_unsettled_transactions

            await _sync_unsettled_transactions()

        mock_finance_service.sync_transactions.assert_awaited_once_with(shop1)

    @pytest.mark.asyncio
    async def test_handles_error_gracefully(self) -> None:
        """Should rollback on error but not crash."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        shop1 = MagicMock(id=uuid.uuid4(), shop_name="Bad Shop")

        shops_result = MagicMock()
        shops_result.scalars.return_value.all.return_value = [shop1]
        mock_session.execute = AsyncMock(return_value=shops_result)

        mock_finance_service = MagicMock()
        mock_finance_service.sync_transactions = AsyncMock(
            side_effect=RuntimeError("timeout")
        )

        with (
            patch("backend.workers.finance_sync.async_session_factory") as mock_factory,
            patch(
                "backend.workers.finance_sync.FinanceService",
                return_value=mock_finance_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.finance_sync import _sync_unsettled_transactions

            await _sync_unsettled_transactions()

        mock_session.rollback.assert_awaited_once()


class TestCeleryTaskRegistration:
    def test_sync_daily_statements_task_name(self) -> None:
        from backend.workers.finance_sync import sync_daily_statements

        assert (
            sync_daily_statements.name
            == "backend.workers.finance_sync.sync_daily_statements"
        )

    def test_sync_unsettled_transactions_task_name(self) -> None:
        from backend.workers.finance_sync import sync_unsettled_transactions

        assert (
            sync_unsettled_transactions.name
            == "backend.workers.finance_sync.sync_unsettled_transactions"
        )


class TestBeatSchedule:
    def test_finance_tasks_in_beat_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "sync-daily-statements" in schedule
        assert "sync-unsettled-transactions" in schedule

    def test_daily_statements_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-daily-statements"]
        assert task["task"] == "backend.workers.finance_sync.sync_daily_statements"

    def test_unsettled_transactions_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-unsettled-transactions"]
        assert (
            task["task"] == "backend.workers.finance_sync.sync_unsettled_transactions"
        )
