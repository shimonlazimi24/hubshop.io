import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestImageUpload:
    @pytest.mark.asyncio
    async def test_upload_image_returns_uri(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {
                "uri": "tos-maliva-i-xxx/image.jpg",
                "url": "https://cdn.tiktok.com/image.jpg",
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.upload_product_image(
                shop_id=uuid.uuid4(),
                image_url="https://example.com/img.jpg",
            )
            assert "uri" in result

    @pytest.mark.asyncio
    async def test_upload_image_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"uri": "x", "url": "y"}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.upload_product_image(
                shop_id=uuid.uuid4(),
                image_url="https://example.com/img.jpg",
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/product/202309/images/upload"

    @pytest.mark.asyncio
    async def test_upload_image_sends_url(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.upload_product_image(
                shop_id=uuid.uuid4(),
                image_url="https://example.com/photo.png",
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["img_url"] == "https://example.com/photo.png"


class TestFileUpload:
    @pytest.mark.asyncio
    async def test_upload_file_returns_uri(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {
                "uri": "tos-maliva-i-xxx/cert.pdf",
                "url": "https://cdn.tiktok.com/cert.pdf",
            }
        }
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.upload_product_file(
                shop_id=uuid.uuid4(),
                file_url="https://example.com/cert.pdf",
                file_name="cert.pdf",
            )
            assert "uri" in result

    @pytest.mark.asyncio
    async def test_upload_file_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"uri": "x", "url": "y"}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.upload_product_file(
                shop_id=uuid.uuid4(),
                file_url="https://example.com/cert.pdf",
                file_name="cert.pdf",
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/product/202309/files/upload"

    @pytest.mark.asyncio
    async def test_upload_file_sends_name(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.upload_product_file(
                shop_id=uuid.uuid4(),
                file_url="https://example.com/doc.pdf",
                file_name="my_document.pdf",
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["name"] == "my_document.pdf"
            assert body["file_url"] == "https://example.com/doc.pdf"
