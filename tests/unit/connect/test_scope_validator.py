"""Tests for platform scope validation."""

import pytest

from backend.modules.connect.services.scope_validator import (
    REQUIRED_SCOPES,
    validate_scopes,
)


class TestScopeValidation:
    def test_developer_all_scopes_present(self) -> None:
        granted = "user.info.basic,user.info.profile,user.info.stats,video.list,video.publish,video.upload,comment.list,comment.list.manage"
        result = validate_scopes("developer", granted)
        assert result["valid"] is True
        assert result["missing"] == []

    def test_developer_missing_scopes(self) -> None:
        granted = "user.info.basic,video.list"
        result = validate_scopes("developer", granted)
        assert result["valid"] is False
        assert "user.info.profile" in result["missing"]
        assert "video.publish" in result["missing"]

    def test_developer_empty_scopes(self) -> None:
        result = validate_scopes("developer", "")
        assert result["valid"] is False
        assert len(result["missing"]) == len(REQUIRED_SCOPES["developer"])

    def test_developer_none_scopes(self) -> None:
        result = validate_scopes("developer", None)
        assert result["valid"] is False

    def test_shop_always_valid(self) -> None:
        result = validate_scopes("shop", None)
        assert result["valid"] is True
        assert result["missing"] == []

    def test_marketing_always_valid(self) -> None:
        result = validate_scopes("marketing", None)
        assert result["valid"] is True
        assert result["missing"] == []

    def test_unknown_platform(self) -> None:
        result = validate_scopes("unknown_platform", "some,scopes")
        assert result["valid"] is True
        assert result["missing"] == []

    def test_required_scopes_defined(self) -> None:
        assert "developer" in REQUIRED_SCOPES
        assert len(REQUIRED_SCOPES["developer"]) == 8
