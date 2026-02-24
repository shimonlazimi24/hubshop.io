"""Tests for analytics DB models - field assignment and utility methods."""

import hashlib
import uuid
from datetime import date

from backend.db.models.analytics import (
    ApiKey,
    Notification,
    NotificationPreference,
    ScheduledReport,
    UnifiedKpiSnapshot,
)


class TestApiKey:
    def test_generate_key(self) -> None:
        """generate_key returns (full_key, prefix, key_hash) with correct structure."""
        full_key, prefix, key_hash = ApiKey.generate_key()

        assert full_key.startswith("frodo_")
        assert prefix == full_key[:12]
        expected_hash = hashlib.sha256(full_key.encode()).hexdigest()
        assert key_hash == expected_hash

    def test_hash_key(self) -> None:
        """hash_key returns a consistent SHA-256 hex digest."""
        raw_key = "frodo_test_raw_key_abc123"
        result = ApiKey.hash_key(raw_key)

        expected = hashlib.sha256(raw_key.encode()).hexdigest()
        assert result == expected
        # Verify determinism
        assert ApiKey.hash_key(raw_key) == result

    def test_generate_and_validate(self) -> None:
        """Hashing the generated full key matches the returned hash."""
        full_key, _prefix, key_hash = ApiKey.generate_key()

        assert ApiKey.hash_key(full_key) == key_hash

    def test_generate_key_uniqueness(self) -> None:
        """Each call to generate_key produces a different key."""
        key_a = ApiKey.generate_key()
        key_b = ApiKey.generate_key()

        assert key_a[0] != key_b[0]
        assert key_a[2] != key_b[2]


class TestUnifiedKpiSnapshot:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()
        snap = UnifiedKpiSnapshot()
        snap.workspace_id = ws_id
        snap.date = date(2026, 2, 20)
        snap.total_orders = 150
        snap.total_revenue = "9999.50"
        snap.average_order_value = "66.66"
        snap.active_campaigns = 3
        snap.total_ad_spend = "500.00"
        snap.total_impressions = 200000
        snap.total_clicks = 8000
        snap.total_videos = 42
        snap.total_views = 1500000
        snap.total_likes = 75000
        snap.total_shares = 3200
        snap.saved_creators = 10
        snap.active_creator_campaigns = 2
        snap.roas = "19.99"
        snap.ctr = "4.00"

        assert snap.workspace_id == ws_id
        assert snap.date == date(2026, 2, 20)
        assert snap.total_orders == 150
        assert snap.total_revenue == "9999.50"
        assert snap.average_order_value == "66.66"
        assert snap.active_campaigns == 3
        assert snap.total_ad_spend == "500.00"
        assert snap.total_impressions == 200000
        assert snap.total_clicks == 8000
        assert snap.total_videos == 42
        assert snap.total_views == 1500000
        assert snap.total_likes == 75000
        assert snap.total_shares == 3200
        assert snap.saved_creators == 10
        assert snap.active_creator_campaigns == 2
        assert snap.roas == "19.99"
        assert snap.ctr == "4.00"


class TestScheduledReport:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()
        user_id = uuid.uuid4()
        modules = ["commerce", "advertising"]
        metrics = {"revenue": True, "ad_spend": True}

        report = ScheduledReport()
        report.workspace_id = ws_id
        report.created_by = user_id
        report.name = "Weekly Sales Report"
        report.description = "A summary of weekly sales."
        report.modules = modules
        report.metrics = metrics
        report.frequency = "WEEKLY"
        report.format = "CSV"
        report.is_active = True

        assert report.workspace_id == ws_id
        assert report.created_by == user_id
        assert report.name == "Weekly Sales Report"
        assert report.description == "A summary of weekly sales."
        assert report.modules == modules
        assert report.metrics == metrics
        assert report.frequency == "WEEKLY"
        assert report.format == "CSV"
        assert report.is_active is True


class TestNotification:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()
        user_id = uuid.uuid4()

        notif = Notification()
        notif.workspace_id = ws_id
        notif.user_id = user_id
        notif.title = "Order shipped"
        notif.message = "Your order #1234 has been shipped."
        notif.notification_type = "SUCCESS"
        notif.module = "commerce"
        notif.action_url = "https://app.frodo.com/orders/1234"
        notif.is_read = False

        assert notif.workspace_id == ws_id
        assert notif.user_id == user_id
        assert notif.title == "Order shipped"
        assert notif.message == "Your order #1234 has been shipped."
        assert notif.notification_type == "SUCCESS"
        assert notif.module == "commerce"
        assert notif.action_url == "https://app.frodo.com/orders/1234"
        assert notif.is_read is False


class TestNotificationPreference:
    def test_fields(self) -> None:
        user_id = uuid.uuid4()

        pref = NotificationPreference()
        pref.user_id = user_id
        pref.module = "advertising"
        pref.channel = "EMAIL"
        pref.is_enabled = True

        assert pref.user_id == user_id
        assert pref.module == "advertising"
        assert pref.channel == "EMAIL"
        assert pref.is_enabled is True

    def test_disabled_preference(self) -> None:
        pref = NotificationPreference()
        pref.user_id = uuid.uuid4()
        pref.module = "system"
        pref.channel = "WEBHOOK"
        pref.is_enabled = False

        assert pref.is_enabled is False
        assert pref.channel == "WEBHOOK"
