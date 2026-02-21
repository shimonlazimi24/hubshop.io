from backend.config import settings


class TestSocialConfig:
    def test_google_oauth_settings_exist(self):
        assert hasattr(settings, "google_client_id")
        assert hasattr(settings, "google_client_secret")
        assert hasattr(settings, "google_redirect_uri")

    def test_tiktok_login_redirect_uri_exists(self):
        assert hasattr(settings, "tiktok_login_redirect_uri")

    def test_google_redirect_uri_default(self):
        assert "google/callback" in settings.google_redirect_uri

    def test_tiktok_login_redirect_uri_default(self):
        assert "tiktok/callback" in settings.tiktok_login_redirect_uri
