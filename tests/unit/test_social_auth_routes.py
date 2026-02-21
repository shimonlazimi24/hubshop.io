from backend.auth.routes import router


class TestSocialAuthRoutes:
    def test_tiktok_login_endpoint_exists(self) -> None:
        paths = [r.path for r in router.routes]
        assert "/auth/tiktok/login" in paths

    def test_google_login_endpoint_exists(self) -> None:
        paths = [r.path for r in router.routes]
        assert "/auth/google/login" in paths

    def test_tiktok_callback_endpoint_exists(self) -> None:
        paths = [r.path for r in router.routes]
        assert "/auth/tiktok/callback" in paths

    def test_google_callback_endpoint_exists(self) -> None:
        paths = [r.path for r in router.routes]
        assert "/auth/google/callback" in paths
