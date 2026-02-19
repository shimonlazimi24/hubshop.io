import hashlib
import hmac

import pytest

from backend.tiktok.shop.client import TikTokShopClient


@pytest.mark.unit
class TestShopHMACSigning:
    def test_signature_generation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify HMAC-SHA256 signature matches expected format."""
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_key", "app123")
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_secret", "secret456")

        client = TikTokShopClient(access_token="token", shop_cipher="cipher")
        path = "/api/products/search"
        params = {"app_key": "app123", "timestamp": "1700000000"}

        sig = client._generate_signature(path, params, "")

        # Manually compute expected signature
        base_string = "secret456" + path + "app_key" + "app123" + "timestamp" + "1700000000" + "" + "secret456"
        expected = hmac.new(
            b"secret456",
            base_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        assert sig == expected

    def test_signature_excludes_sign_and_access_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_key", "app123")
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_secret", "secret456")

        client = TikTokShopClient(access_token="token")
        params = {
            "app_key": "app123",
            "timestamp": "1700000000",
            "sign": "should_be_excluded",
            "access_token": "should_be_excluded",
        }

        sig = client._generate_signature("/api/test", params, "")

        # Same as without sign/access_token
        params_clean = {"app_key": "app123", "timestamp": "1700000000"}
        sig_clean = client._generate_signature("/api/test", params_clean, "")

        assert sig == sig_clean

    def test_signature_includes_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_key", "app123")
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_secret", "secret456")

        client = TikTokShopClient(access_token="token")
        params = {"app_key": "app123", "timestamp": "1700000000"}

        sig_no_body = client._generate_signature("/api/test", params, "")
        sig_with_body = client._generate_signature("/api/test", params, '{"key":"value"}')

        assert sig_no_body != sig_with_body

    def test_signature_params_sorted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_key", "app123")
        monkeypatch.setattr("backend.tiktok.shop.client.settings.tiktok_shop_app_secret", "secret456")

        client = TikTokShopClient(access_token="token")

        params_a = {"app_key": "app123", "timestamp": "1700000000", "z_param": "z", "a_param": "a"}
        params_b = {"z_param": "z", "a_param": "a", "app_key": "app123", "timestamp": "1700000000"}

        assert client._generate_signature("/api/test", params_a, "") == client._generate_signature(
            "/api/test", params_b, ""
        )
