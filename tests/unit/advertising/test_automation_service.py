"""Tests for AutomationService — list, create, update, delete automation rules."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.automation_service import AutomationService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_account_service(
    sample_ad_account: SimpleNamespace, mock_gateway: AsyncMock
):
    with patch(
        "backend.modules.advertising.services.automation_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestListRules:
    @pytest.mark.asyncio
    async def test_list_rules(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"rule_id": "r1", "rule_name": "Pause low performers"},
                ]
            }
        }

        service = AutomationService(mock_session)
        result = await service.list_rules(
            sample_ad_account.workspace_id, sample_ad_account
        )

        assert len(result["list"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id

    @pytest.mark.asyncio
    async def test_list_rules_with_pagination(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = AutomationService(mock_session)
        await service.list_rules(
            sample_ad_account.workspace_id,
            sample_ad_account,
            page=2,
            page_size=10,
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "2"
        assert call_params["page_size"] == "10"


class TestCreateRule:
    @pytest.mark.asyncio
    async def test_create_rule(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"rule_id": "r_new", "rule_name": "Auto Budget"}
        }

        rule_config = {
            "rule_name": "Auto Budget",
            "conditions": [{"metric": "cpa", "operator": ">", "value": 10}],
            "actions": [{"type": "pause"}],
        }

        service = AutomationService(mock_session)
        result = await service.create_rule(
            sample_ad_account.workspace_id,
            sample_ad_account,
            rule_config=rule_config,
        )

        assert result["rule_id"] == "r_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["rule_name"] == "Auto Budget"
        assert call_body["conditions"][0]["metric"] == "cpa"


class TestUpdateRule:
    @pytest.mark.asyncio
    async def test_update_rule(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"rule_id": "r1"}}

        service = AutomationService(mock_session)
        result = await service.update_rule(
            sample_ad_account.workspace_id,
            sample_ad_account,
            rule_id="r1",
            updates={"rule_name": "Updated Rule"},
        )

        assert result["rule_id"] == "r1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["rule_id"] == "r1"
        assert call_body["rule_name"] == "Updated Rule"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestDeleteRule:
    @pytest.mark.asyncio
    async def test_delete_rule(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        service = AutomationService(mock_session)
        result = await service.delete_rule(
            sample_ad_account.workspace_id,
            sample_ad_account,
            rule_id="r1",
        )

        assert result == {}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["rule_id"] == "r1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
