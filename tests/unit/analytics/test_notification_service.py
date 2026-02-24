"""Tests for NotificationService - CRUD, read status, preferences."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.analytics import Notification, NotificationPreference
from backend.modules.analytics.services.notification_service import NotificationService


class TestCreateNotification:
    @pytest.mark.asyncio
    async def test_create_notification(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        workspace_id = uuid.uuid4()
        user_id = uuid.uuid4()

        service = NotificationService(session)
        notification = await service.create_notification(
            workspace_id,
            user_id,
            title="Order Received",
            message="New order #1234 received",
            notification_type="SUCCESS",
            module="commerce",
            action_url="/orders/1234",
        )

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert isinstance(added, Notification)
        assert added.workspace_id == workspace_id
        assert added.user_id == user_id
        assert added.title == "Order Received"
        assert added.message == "New order #1234 received"
        assert added.notification_type == "SUCCESS"
        assert added.module == "commerce"
        assert added.action_url == "/orders/1234"


class TestListNotifications:
    @pytest.fixture
    def user_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_list_notifications_paginated(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 5

        n1 = SimpleNamespace(id=uuid.uuid4(), title="Notif 1")
        n2 = SimpleNamespace(id=uuid.uuid4(), title="Notif 2")
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [n1, n2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = NotificationService(session)
        result = await service.list_notifications(
            user_id, workspace_id=workspace_id, page=1, page_size=2
        )

        assert result.total == 5
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 2
        assert result.total_pages == 3

    @pytest.mark.asyncio
    async def test_list_notifications_filtered_by_read_status(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        n1 = SimpleNamespace(id=uuid.uuid4(), title="Unread 1", is_read=False)
        n2 = SimpleNamespace(id=uuid.uuid4(), title="Unread 2", is_read=False)
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [n1, n2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = NotificationService(session)
        result = await service.list_notifications(
            user_id, workspace_id=workspace_id, is_read=False
        )

        assert result.total == 2
        assert len(result.items) == 2
        # Verify the execute was called (filter is applied at query construction)
        assert session.execute.call_count == 2


class TestMarkRead:
    @pytest.mark.asyncio
    async def test_mark_read(self) -> None:
        user_id = uuid.uuid4()
        notification_id = uuid.uuid4()
        notification = SimpleNamespace(
            id=notification_id,
            user_id=user_id,
            is_read=False,
            read_at=None,
        )

        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = notification
        session.execute.return_value = result_mock

        service = NotificationService(session)
        result = await service.mark_read(notification_id, user_id)

        assert result is not None
        assert result.is_read is True
        assert result.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_read_already_read(self) -> None:
        user_id = uuid.uuid4()
        notification_id = uuid.uuid4()
        read_time = datetime(2026, 2, 19, 10, 0, 0, tzinfo=UTC)
        notification = SimpleNamespace(
            id=notification_id,
            user_id=user_id,
            is_read=True,
            read_at=read_time,
        )

        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = notification
        session.execute.return_value = result_mock

        service = NotificationService(session)
        result = await service.mark_read(notification_id, user_id)

        assert result is not None
        # Should remain unchanged
        assert result.is_read is True
        assert result.read_at == read_time

    @pytest.mark.asyncio
    async def test_mark_read_not_found(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = NotificationService(session)
        result = await service.mark_read(uuid.uuid4(), uuid.uuid4())

        assert result is None


class TestMarkAllRead:
    @pytest.mark.asyncio
    async def test_mark_all_read(self) -> None:
        session = AsyncMock()
        update_result = MagicMock()
        update_result.rowcount = 7
        session.execute.return_value = update_result

        user_id = uuid.uuid4()
        workspace_id = uuid.uuid4()

        service = NotificationService(session)
        count = await service.mark_all_read(user_id, workspace_id)

        assert count == 7
        assert session.execute.called


class TestGetUnreadCount:
    @pytest.mark.asyncio
    async def test_get_unread_count(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one.return_value = 12
        session.execute.return_value = result_mock

        user_id = uuid.uuid4()
        workspace_id = uuid.uuid4()

        service = NotificationService(session)
        count = await service.get_unread_count(user_id, workspace_id)

        assert count == 12


class TestPreferences:
    @pytest.fixture
    def user_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_get_preferences(self, user_id: uuid.UUID) -> None:
        session = AsyncMock()
        pref1 = SimpleNamespace(
            user_id=user_id, module="commerce", channel="IN_APP", is_enabled=True
        )
        pref2 = SimpleNamespace(
            user_id=user_id, module="advertising", channel="EMAIL", is_enabled=False
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [pref1, pref2]
        session.execute.return_value = result_mock

        service = NotificationService(session)
        prefs = await service.get_preferences(user_id)

        assert len(prefs) == 2
        assert prefs[0].module == "commerce"
        assert prefs[1].channel == "EMAIL"

    @pytest.mark.asyncio
    async def test_update_preference_creates_new(self, user_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = NotificationService(session)
        pref = await service.update_preference(user_id, "commerce", "EMAIL", True)

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert isinstance(added, NotificationPreference)
        assert added.user_id == user_id
        assert added.module == "commerce"
        assert added.channel == "EMAIL"
        assert added.is_enabled is True

    @pytest.mark.asyncio
    async def test_update_preference_updates_existing(self, user_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.add = MagicMock()

        existing = SimpleNamespace(
            id=uuid.uuid4(),
            user_id=user_id,
            module="commerce",
            channel="EMAIL",
            is_enabled=True,
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        session.execute.return_value = result_mock

        service = NotificationService(session)
        pref = await service.update_preference(user_id, "commerce", "EMAIL", False)

        assert pref.is_enabled is False
        # Should NOT add when updating existing
        assert not session.add.called
