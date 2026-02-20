"""Tests for ReportService - CRUD, pagination, next-run calculation."""

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.analytics import ScheduledReport
from backend.modules.analytics.services.report_service import ReportService


class TestCreateReport:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_create_report(self, mock_session: AsyncMock) -> None:
        workspace_id = uuid.uuid4()
        user_id = uuid.uuid4()

        service = ReportService(mock_session)
        report = await service.create_report(
            workspace_id,
            user_id,
            name="Weekly Sales",
            description="Sales summary",
            modules=["commerce", "advertising"],
            frequency="WEEKLY",
            format="CSV",
        )

        assert mock_session.add.called
        added = mock_session.add.call_args_list[0][0][0]
        assert isinstance(added, ScheduledReport)
        assert added.workspace_id == workspace_id
        assert added.created_by == user_id
        assert added.name == "Weekly Sales"
        assert added.description == "Sales summary"
        assert added.modules == ["commerce", "advertising"]
        assert added.frequency == "WEEKLY"
        assert added.format == "CSV"
        assert added.is_active is True
        assert added.next_run_at is not None


class TestListReports:
    @pytest.mark.asyncio
    async def test_list_reports_paginated(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 3

        r1 = SimpleNamespace(id=uuid.uuid4(), name="Report 1")
        r2 = SimpleNamespace(id=uuid.uuid4(), name="Report 2")
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [r1, r2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = ReportService(session)
        result = await service.list_reports(uuid.uuid4(), page=1, page_size=2)

        assert result.total == 3
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 2
        assert result.total_pages == 2

    @pytest.mark.asyncio
    async def test_list_reports_empty(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = ReportService(session)
        result = await service.list_reports(uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0


class TestGetReport:
    @pytest.mark.asyncio
    async def test_get_report_found(self) -> None:
        report = SimpleNamespace(id=uuid.uuid4(), name="My Report")
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = report
        session.execute.return_value = result_mock

        service = ReportService(session)
        found = await service.get_report(report.id)

        assert found is not None
        assert found.name == "My Report"

    @pytest.mark.asyncio
    async def test_get_report_not_found(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = ReportService(session)
        found = await service.get_report(uuid.uuid4())

        assert found is None


class TestUpdateReport:
    @pytest.mark.asyncio
    async def test_update_report_fields(self) -> None:
        session = AsyncMock()
        report = SimpleNamespace(
            id=uuid.uuid4(),
            name="Old Name",
            description="Old desc",
            modules=["commerce"],
            frequency="WEEKLY",
            format="CSV",
            is_active=True,
            next_run_at=datetime.now(tz=timezone.utc),
        )

        service = ReportService(session)
        updated = await service.update_report(
            report,
            name="New Name",
            frequency="DAILY",
            is_active=False,
        )

        assert updated.name == "New Name"
        assert updated.frequency == "DAILY"
        assert updated.is_active is False
        # next_run_at should be recalculated for new frequency
        assert updated.next_run_at is not None


class TestDeleteReport:
    @pytest.mark.asyncio
    async def test_delete_report_found(self) -> None:
        session = AsyncMock()
        report = SimpleNamespace(id=uuid.uuid4(), name="To Delete")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = report
        session.execute.return_value = result_mock
        session.delete = AsyncMock()

        service = ReportService(session)
        deleted = await service.delete_report(report.id)

        assert deleted is True
        session.delete.assert_awaited_once_with(report)

    @pytest.mark.asyncio
    async def test_delete_report_not_found(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = ReportService(session)
        deleted = await service.delete_report(uuid.uuid4())

        assert deleted is False


class TestCalculateNextRun:
    def test_calculate_next_run_daily(self) -> None:
        now = datetime(2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc)
        result = ReportService._calculate_next_run("DAILY", now)
        assert result == now + timedelta(days=1)

    def test_calculate_next_run_weekly(self) -> None:
        now = datetime(2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc)
        result = ReportService._calculate_next_run("WEEKLY", now)
        assert result == now + timedelta(weeks=1)

    def test_calculate_next_run_monthly(self) -> None:
        now = datetime(2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc)
        result = ReportService._calculate_next_run("MONTHLY", now)
        assert result == now + timedelta(days=30)
