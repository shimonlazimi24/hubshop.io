"""Tests for promotion sync Celery tasks."""

from backend.workers.promotion_sync import sync_all_coupons, sync_all_promotions


class TestSyncAllPromotions:
    def test_task_exists(self) -> None:
        assert (
            sync_all_promotions.name
            == "backend.workers.promotion_sync.sync_all_promotions"
        )

    def test_task_is_callable(self) -> None:
        assert callable(sync_all_promotions)


class TestSyncAllCoupons:
    def test_task_exists(self) -> None:
        assert (
            sync_all_coupons.name == "backend.workers.promotion_sync.sync_all_coupons"
        )

    def test_task_is_callable(self) -> None:
        assert callable(sync_all_coupons)
