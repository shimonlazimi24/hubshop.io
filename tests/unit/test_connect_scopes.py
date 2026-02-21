class TestConnectScopes:
    def test_developer_scopes_include_publish(self) -> None:
        from backend.modules.connect.routes import DEVELOPER_SCOPES

        assert "video.publish" in DEVELOPER_SCOPES
        assert "video.upload" in DEVELOPER_SCOPES
        assert "comment.list" in DEVELOPER_SCOPES
        assert "user.info.stats" in DEVELOPER_SCOPES
        assert "user.info.basic" in DEVELOPER_SCOPES

    def test_developer_scopes_is_comma_separated(self) -> None:
        from backend.modules.connect.routes import DEVELOPER_SCOPES

        assert "," in DEVELOPER_SCOPES
        parts = DEVELOPER_SCOPES.split(",")
        assert len(parts) == 8
