import hashlib
import hmac

import pytest

from backend.modules.webhooks.verification import (
    verify_developer_webhook,
    verify_shop_webhook,
)


@pytest.mark.unit
class TestShopWebhookVerification:
    def test_valid_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_shop_app_key", "app_key"
        )
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_shop_app_secret", "app_secret"
        )

        body = b'{"type":"ORDER_STATUS_CHANGE","data":{}}'
        sig = hmac.new(
            b"app_secret",
            ("app_key" + body.decode()).encode(),
            hashlib.sha256,
        ).hexdigest()

        assert verify_shop_webhook(body, sig)

    def test_invalid_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_shop_app_key", "app_key"
        )
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_shop_app_secret", "app_secret"
        )

        body = b'{"type":"ORDER_STATUS_CHANGE"}'
        assert not verify_shop_webhook(body, "invalid_signature")

    def test_tampered_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_shop_app_key", "app_key"
        )
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_shop_app_secret", "app_secret"
        )

        original_body = b'{"amount":"100"}'
        sig = hmac.new(
            b"app_secret",
            ("app_key" + original_body.decode()).encode(),
            hashlib.sha256,
        ).hexdigest()

        tampered_body = b'{"amount":"999"}'
        assert not verify_shop_webhook(tampered_body, sig)


@pytest.mark.unit
class TestDeveloperWebhookVerification:
    def test_valid_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_developer_client_secret",
            "client_secret",
        )

        body = b'{"event":"video.publish"}'
        timestamp = "1700000000"
        sig = hmac.new(
            b"client_secret",
            f"{timestamp}.{body.decode()}".encode(),
            hashlib.sha256,
        ).hexdigest()

        header = f"t={timestamp},s={sig}"
        assert verify_developer_webhook(body, header)

    def test_invalid_signature(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_developer_client_secret",
            "client_secret",
        )

        body = b'{"event":"video.publish"}'
        header = "t=1700000000,s=invalid_sig"
        assert not verify_developer_webhook(body, header)

    def test_malformed_header(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "backend.modules.webhooks.verification.settings.tiktok_developer_client_secret",
            "client_secret",
        )

        body = b'{"event":"video.publish"}'
        assert not verify_developer_webhook(body, "malformed")
        assert not verify_developer_webhook(body, "")
        assert not verify_developer_webhook(body, "t=,s=")
