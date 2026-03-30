"""Tests for enhanced CustomerServiceService — agent settings, CS performance, sessions."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.customer_service import CustomerServiceService


class TestGetAgentSettings:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.mark.asyncio
    async def test_get_agent_settings_returns_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "online_hours": {"start": "09:00", "end": "18:00"},
                "auto_reply_enabled": True,
            }
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.commerce.services.customer_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = CustomerServiceService(mock_session)
            result = await service.get_agent_settings(sample_shop)

        assert result == {
            "online_hours": {"start": "09:00", "end": "18:00"},
            "auto_reply_enabled": True,
        }
        mock_gateway.get.assert_awaited_once_with(
            "/customer_service/202309/agents/settings"
        )

    @pytest.mark.asyncio
    async def test_get_agent_settings_empty_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {}

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.commerce.services.customer_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = CustomerServiceService(mock_session)
            result = await service.get_agent_settings(sample_shop)

        assert result == {}


class TestUpdateAgentSettings:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.mark.asyncio
    async def test_update_agent_settings_posts_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"success": True}}

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        settings_payload = {
            "auto_reply_enabled": True,
            "greeting_message": "Hello!",
        }

        with patch(
            "backend.modules.commerce.services.customer_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = CustomerServiceService(mock_session)
            result = await service.update_agent_settings(
                sample_shop, settings=settings_payload
            )

        assert result == {"success": True}
        mock_gateway.post.assert_awaited_once_with(
            "/customer_service/202309/agents/settings",
            json_body=settings_payload,
        )


class TestGetCsPerformance:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.mark.asyncio
    async def test_get_cs_performance_returns_metrics(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "response_rate_24h": "0.95",
                "resolution_rate": "0.88",
                "total_conversations": 150,
            }
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.commerce.services.customer_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = CustomerServiceService(mock_session)
            result = await service.get_cs_performance(sample_shop)

        assert result["response_rate_24h"] == "0.95"
        assert result["total_conversations"] == 150
        mock_gateway.get.assert_awaited_once_with(
            "/customer_service/202309/performance"
        )


class TestUploadImage:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.mark.asyncio
    async def test_upload_image_returns_url(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {
            "data": {"url": "https://example.com/uploaded.jpg"}
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.commerce.services.customer_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = CustomerServiceService(mock_session)
            result = await service.upload_image(sample_shop, image_data=b"fake_image")

        assert result == {"url": "https://example.com/uploaded.jpg"}
        mock_gateway.post.assert_awaited_once_with(
            "/customer_service/202309/media/upload",
            json_body={"data": "base64_placeholder"},
        )


class TestSearchSessions:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.mark.asyncio
    async def test_search_sessions_with_filters(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {"sessions": [{"id": "s1"}, {"id": "s2"}]}
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        filters = {"status": "open", "page_size": 10}

        with patch(
            "backend.modules.commerce.services.customer_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = CustomerServiceService(mock_session)
            result = await service.search_sessions(sample_shop, filters=filters)

        assert "sessions" in result
        assert len(result["sessions"]) == 2
        mock_gateway.get.assert_awaited_once_with(
            "/customer_service/202309/sessions",
            params={"status": "open", "page_size": "10"},
        )


class TestCsPerformanceSnapshotModel:
    def test_model_has_required_columns(self) -> None:
        from backend.db.models.customer_service import CsPerformanceSnapshot

        snapshot = CsPerformanceSnapshot(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            response_rate_24h="0.95",
            resolution_rate="0.88",
            satisfaction_score="4.5",
            total_conversations=150,
            avg_response_time_seconds=300,
        )

        assert snapshot.response_rate_24h == "0.95"
        assert snapshot.resolution_rate == "0.88"
        assert snapshot.satisfaction_score == "4.5"
        assert snapshot.total_conversations == 150
        assert snapshot.avg_response_time_seconds == 300

    def test_model_tablename(self) -> None:
        from backend.db.models.customer_service import CsPerformanceSnapshot

        assert CsPerformanceSnapshot.__tablename__ == "cs_performance_snapshots"


class TestUpdateAgentSettingsSchema:
    def test_schema_accepts_all_fields(self) -> None:
        from backend.modules.commerce.schemas import UpdateAgentSettingsRequest

        req = UpdateAgentSettingsRequest(
            online_hours={"start": "09:00", "end": "18:00"},
            auto_reply_enabled=True,
            auto_reply_message="We'll respond soon!",
            greeting_message="Welcome!",
        )
        assert req.auto_reply_enabled is True
        assert req.greeting_message == "Welcome!"

    def test_schema_all_fields_optional(self) -> None:
        from backend.modules.commerce.schemas import UpdateAgentSettingsRequest

        req = UpdateAgentSettingsRequest()
        assert req.online_hours is None
        assert req.auto_reply_enabled is None
        assert req.auto_reply_message is None
        assert req.greeting_message is None

    def test_schema_partial_update(self) -> None:
        from backend.modules.commerce.schemas import UpdateAgentSettingsRequest

        req = UpdateAgentSettingsRequest(auto_reply_enabled=False)
        assert req.auto_reply_enabled is False
        assert req.greeting_message is None


class TestCsPerformanceSnapshotInModelsInit:
    def test_model_importable_from_init(self) -> None:
        from backend.db.models import CsPerformanceSnapshot

        assert CsPerformanceSnapshot is not None
