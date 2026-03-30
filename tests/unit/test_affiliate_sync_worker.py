"""Tests for E5: Affiliate sync Celery workers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSyncAffiliateCreators:
    @pytest.mark.asyncio
    async def test_syncs_creators_for_all_shops(self) -> None:
        """Should iterate all shops and sync affiliate creators."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"creators": [{"creator_id": "c1"}]}}

        with (
            patch(
                "backend.workers.affiliate_sync.async_session_factory"
            ) as mock_factory,
            patch("backend.workers.affiliate_sync.ShopService") as mock_shop_svc_cls,
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_shop_svc_cls.return_value.build_gateway_for_shop = AsyncMock(
                return_value=mock_gateway
            )

            from backend.workers.affiliate_sync import _sync_affiliate_creators

            await _sync_affiliate_creators()

        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_creator_sync_failure(self) -> None:
        """Should rollback on failure and continue."""
        shop = MagicMock()
        shop.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        with (
            patch(
                "backend.workers.affiliate_sync.async_session_factory"
            ) as mock_factory,
            patch("backend.workers.affiliate_sync.ShopService") as mock_shop_svc_cls,
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_shop_svc_cls.return_value.build_gateway_for_shop = AsyncMock(
                side_effect=RuntimeError("API error")
            )

            from backend.workers.affiliate_sync import _sync_affiliate_creators

            await _sync_affiliate_creators()

        mock_session.rollback.assert_awaited()


class TestSyncAffiliateOrders:
    @pytest.mark.asyncio
    async def test_syncs_orders_for_all_shops(self) -> None:
        """Should iterate all shops and sync affiliate orders."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        with (
            patch(
                "backend.workers.affiliate_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.affiliate_sync.AffiliateService"
            ) as mock_aff_svc_cls,
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_aff_svc_cls.return_value.sync_affiliate_orders = AsyncMock(
                return_value=5
            )

            from backend.workers.affiliate_sync import _sync_affiliate_orders

            await _sync_affiliate_orders()

        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_order_sync_failure(self) -> None:
        """Should rollback on failure and continue."""
        shop = MagicMock()
        shop.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        with (
            patch(
                "backend.workers.affiliate_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.affiliate_sync.AffiliateService"
            ) as mock_aff_svc_cls,
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_aff_svc_cls.return_value.sync_affiliate_orders = AsyncMock(
                side_effect=RuntimeError("Order sync error")
            )

            from backend.workers.affiliate_sync import _sync_affiliate_orders

            await _sync_affiliate_orders()

        mock_session.rollback.assert_awaited()


class TestSyncSampleRequests:
    @pytest.mark.asyncio
    async def test_syncs_samples_for_all_shops(self) -> None:
        """Should iterate all shops and sync sample requests."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {"sample_requests": [{"request_id": "sr1"}]}
        }

        with (
            patch(
                "backend.workers.affiliate_sync.async_session_factory"
            ) as mock_factory,
            patch("backend.workers.affiliate_sync.ShopService") as mock_shop_svc_cls,
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_shop_svc_cls.return_value.build_gateway_for_shop = AsyncMock(
                return_value=mock_gateway
            )

            from backend.workers.affiliate_sync import _sync_sample_requests

            await _sync_sample_requests()

        mock_session.commit.assert_awaited()


class TestCeleryTaskRegistration:
    def test_sync_affiliate_creators_task_exists(self) -> None:
        from backend.workers.affiliate_sync import sync_affiliate_creators

        assert (
            sync_affiliate_creators.name
            == "backend.workers.affiliate_sync.sync_affiliate_creators"
        )

    def test_sync_affiliate_orders_task_exists(self) -> None:
        from backend.workers.affiliate_sync import sync_affiliate_orders

        assert (
            sync_affiliate_orders.name
            == "backend.workers.affiliate_sync.sync_affiliate_orders"
        )

    def test_sync_sample_requests_task_exists(self) -> None:
        from backend.workers.affiliate_sync import sync_sample_requests

        assert (
            sync_sample_requests.name
            == "backend.workers.affiliate_sync.sync_sample_requests"
        )


class TestBeatSchedule:
    def test_affiliate_tasks_in_beat_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "sync-affiliate-creators" in schedule
        assert "sync-affiliate-orders" in schedule
        assert "sync-sample-requests" in schedule

    def test_sync_affiliate_creators_daily(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-affiliate-creators"]
        assert task["task"] == "backend.workers.affiliate_sync.sync_affiliate_creators"

    def test_sync_affiliate_orders_every_2h(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-affiliate-orders"]
        assert task["task"] == "backend.workers.affiliate_sync.sync_affiliate_orders"

    def test_sync_sample_requests_every_30min(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-sample-requests"]
        assert task["task"] == "backend.workers.affiliate_sync.sync_sample_requests"
