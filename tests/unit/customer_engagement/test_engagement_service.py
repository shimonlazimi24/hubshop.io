"""Tests for EngagementService — templates, tasks, permissions."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.customer_engagement.services.engagement_service import (
    EngagementService,
)


class TestGetTemplates:
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
    async def test_get_templates_returns_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "templates": [
                    {"id": "t1", "name": "Welcome"},
                    {"id": "t2", "name": "Follow-up"},
                ]
            }
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.customer_engagement.services.engagement_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = EngagementService(mock_session)
            result = await service.get_templates(sample_shop)

        assert "templates" in result
        assert len(result["templates"]) == 2
        mock_gateway.get.assert_awaited_once_with(
            "/customer_engagement/202309/templates"
        )

    @pytest.mark.asyncio
    async def test_get_templates_empty(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {}

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.customer_engagement.services.engagement_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = EngagementService(mock_session)
            result = await service.get_templates(sample_shop)

        assert result == {}


class TestCreateTask:
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
    async def test_create_task_posts_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {
            "data": {"task_id": "task_001", "status": "created"}
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        task_data = {"template_id": "t1", "audience": "all_buyers"}

        with patch(
            "backend.modules.customer_engagement.services.engagement_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = EngagementService(mock_session)
            result = await service.create_task(sample_shop, task_data=task_data)

        assert result["task_id"] == "task_001"
        mock_gateway.post.assert_awaited_once_with(
            "/customer_engagement/202309/tasks",
            json_body=task_data,
        )


class TestCreateCustomTask:
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
    async def test_create_custom_task_posts_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {
            "data": {"task_id": "custom_001", "status": "created"}
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        task_data = {"message": "Custom promo", "audience_ids": ["a1"]}

        with patch(
            "backend.modules.customer_engagement.services.engagement_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = EngagementService(mock_session)
            result = await service.create_custom_task(sample_shop, task_data=task_data)

        assert result["task_id"] == "custom_001"
        mock_gateway.post.assert_awaited_once_with(
            "/customer_engagement/202309/tasks/custom",
            json_body=task_data,
        )


class TestGetTaskPerformance:
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
    async def test_get_task_performance_returns_metrics(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "sent_count": 100,
                "open_rate": "0.45",
                "click_rate": "0.12",
            }
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.customer_engagement.services.engagement_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = EngagementService(mock_session)
            result = await service.get_task_performance(sample_shop, task_id="task_001")

        assert result["sent_count"] == 100
        mock_gateway.get.assert_awaited_once_with(
            "/customer_engagement/202309/tasks/task_001/performance"
        )


class TestGetPermissions:
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
    async def test_get_permissions_returns_data(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {"can_send_messages": True, "daily_quota": 500}
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with patch(
            "backend.modules.customer_engagement.services.engagement_service.ShopService",
            return_value=mock_shop_service,
        ):
            service = EngagementService(mock_session)
            result = await service.get_permissions(sample_shop)

        assert result["can_send_messages"] is True
        mock_gateway.get.assert_awaited_once_with(
            "/customer_engagement/202309/permissions"
        )


class TestEngagementSchemas:
    def test_create_engagement_task_request(self) -> None:
        from backend.modules.customer_engagement.schemas import (
            CreateEngagementTaskRequest,
        )

        req = CreateEngagementTaskRequest(
            shop_id="shop_001",
            template_id="t1",
            audience="all_buyers",
        )
        assert req.shop_id == "shop_001"
        assert req.template_id == "t1"

    def test_custom_engagement_task_request(self) -> None:
        from backend.modules.customer_engagement.schemas import (
            CustomEngagementTaskRequest,
        )

        req = CustomEngagementTaskRequest(
            shop_id="shop_001",
            message="Custom promo message",
            audience_ids=["a1", "a2"],
        )
        assert req.message == "Custom promo message"
        assert len(req.audience_ids) == 2

    def test_engagement_task_response(self) -> None:
        from backend.modules.customer_engagement.schemas import (
            EngagementTaskResponse,
        )

        resp = EngagementTaskResponse(task_id="t1", status="created")
        assert resp.task_id == "t1"

    def test_engagement_template_response(self) -> None:
        from backend.modules.customer_engagement.schemas import (
            EngagementTemplateResponse,
        )

        resp = EngagementTemplateResponse(
            template_id="tpl_1", name="Welcome", content="Hi there!"
        )
        assert resp.template_id == "tpl_1"


class TestEngagementModels:
    def test_engagement_task_model(self) -> None:
        from backend.db.models.customer_engagement import EngagementTask

        task = EngagementTask(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_task_id="task_001",
            template_id="t1",
            status="created",
            audience="all_buyers",
        )
        assert task.platform_task_id == "task_001"
        assert task.status == "created"

    def test_engagement_task_tablename(self) -> None:
        from backend.db.models.customer_engagement import EngagementTask

        assert EngagementTask.__tablename__ == "engagement_tasks"

    def test_engagement_template_model(self) -> None:
        from backend.db.models.customer_engagement import EngagementTemplate

        template = EngagementTemplate(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_template_id="tpl_001",
            name="Welcome",
            content="Hello!",
        )
        assert template.platform_template_id == "tpl_001"
        assert template.name == "Welcome"

    def test_engagement_template_tablename(self) -> None:
        from backend.db.models.customer_engagement import EngagementTemplate

        assert EngagementTemplate.__tablename__ == "engagement_templates"


class TestEngagementModelsInInit:
    def test_engagement_task_importable(self) -> None:
        from backend.db.models import EngagementTask

        assert EngagementTask is not None

    def test_engagement_template_importable(self) -> None:
        from backend.db.models import EngagementTemplate

        assert EngagementTemplate is not None


class TestEngagementRouterRegistration:
    def test_engagement_router_registered_in_main(self) -> None:
        from backend.main import app

        routes = [route.path for route in app.routes]
        # Check that engagement routes are registered
        assert any("/engagement" in r for r in routes)
