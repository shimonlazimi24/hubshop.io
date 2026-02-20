"""Tests for IdentityService — create, delete, list, detail, posts."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.identity_service import IdentityService


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
        "backend.modules.advertising.services.identity_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestCreateIdentity:
    @pytest.mark.asyncio
    async def test_create_identity(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"identity_id": "id_new", "display_name": "Brand Page"}
        }

        identity_config = {
            "display_name": "Brand Page",
            "profile_image_url": "https://example.com/img.png",
        }

        service = IdentityService(mock_session)
        result = await service.create_identity(
            sample_ad_account.workspace_id,
            sample_ad_account,
            identity_config=identity_config,
        )

        assert result["identity_id"] == "id_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_body["display_name"] == "Brand Page"


class TestDeleteIdentity:
    @pytest.mark.asyncio
    async def test_delete_identity(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        service = IdentityService(mock_session)
        result = await service.delete_identity(
            sample_ad_account.workspace_id,
            sample_ad_account,
            identity_id="id1",
        )

        assert result == {}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["identity_id"] == "id1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestListIdentities:
    @pytest.mark.asyncio
    async def test_list_identities(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"identity_id": "id1", "display_name": "Brand Page"},
                ]
            }
        }

        service = IdentityService(mock_session)
        result = await service.list_identities(
            sample_ad_account.workspace_id, sample_ad_account
        )

        assert len(result["list"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetIdentityDetail:
    @pytest.mark.asyncio
    async def test_get_identity_detail(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "identity_id": "id1",
                "display_name": "Brand Page",
                "profile_image_url": "https://example.com/img.png",
            }
        }

        service = IdentityService(mock_session)
        result = await service.get_identity_detail(
            sample_ad_account.workspace_id,
            sample_ad_account,
            identity_id="id1",
        )

        assert result["identity_id"] == "id1"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["identity_id"] == "id1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id


class TestGetIdentityPosts:
    @pytest.mark.asyncio
    async def test_get_identity_posts(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "posts": [
                    {"post_id": "p1", "title": "Summer Sale"},
                ]
            }
        }

        service = IdentityService(mock_session)
        result = await service.get_identity_posts(
            sample_ad_account.workspace_id,
            sample_ad_account,
            identity_id="id1",
        )

        assert len(result["posts"]) == 1
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["identity_id"] == "id1"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
