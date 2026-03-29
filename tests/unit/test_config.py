"""Tests for config secret validation (backend/config.py)."""

import pytest
from pydantic import ValidationError

from backend.config import Settings


@pytest.mark.unit
class TestConfigSecretValidation:
    """Test the _check_production_secrets model validator."""

    def test_production_with_change_me_secret_key_raises(self) -> None:
        """Production mode with default SECRET_KEY should raise ValueError."""
        with pytest.raises(ValidationError, match="SECRET_KEY"):
            Settings(
                app_env="production",
                secret_key="change-me",
                jwt_secret_key="a-real-secret-key-for-jwt",
                token_vault_key="YS1yZWFsLTMyLWJ5dGUtdmF1bHQta2V5LTEyMzQ=",
            )

    def test_production_with_change_me_jwt_key_raises(self) -> None:
        """Production mode with default JWT_SECRET_KEY should raise ValueError."""
        with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
            Settings(
                app_env="production",
                secret_key="a-real-secret-key",
                jwt_secret_key="change-me",
                token_vault_key="YS1yZWFsLTMyLWJ5dGUtdmF1bHQta2V5LTEyMzQ=",
            )

    def test_production_with_change_me_vault_key_raises(self) -> None:
        """Production mode with default TOKEN_VAULT_KEY should raise ValueError."""
        with pytest.raises(ValidationError, match="TOKEN_VAULT_KEY"):
            Settings(
                app_env="production",
                secret_key="a-real-secret-key",
                jwt_secret_key="a-real-jwt-key",
                token_vault_key="change-me-base64-encoded-32-byte-key",
            )

    def test_production_with_multiple_insecure_keys_mentions_all(self) -> None:
        """All insecure keys should be mentioned in the error."""
        with pytest.raises(ValidationError, match="SECRET_KEY") as exc_info:
            Settings(
                app_env="production",
                secret_key="change-me",
                jwt_secret_key="change-me",
                token_vault_key="change-me-base64-encoded-32-byte-key",
            )
        error_text = str(exc_info.value)
        assert "JWT_SECRET_KEY" in error_text
        assert "TOKEN_VAULT_KEY" in error_text

    def test_development_with_change_me_secrets_succeeds(self) -> None:
        """Development mode should allow default secrets without error."""
        config = Settings(
            app_env="development",
            secret_key="change-me",
            jwt_secret_key="change-me",
            token_vault_key="change-me-base64-encoded-32-byte-key",
        )
        assert config.app_env == "development"
        assert not config.is_production

    def test_production_with_real_secrets_succeeds(self) -> None:
        """Production mode with all real secrets should succeed."""
        config = Settings(
            app_env="production",
            secret_key="super-secure-secret-key-2024",
            jwt_secret_key="super-secure-jwt-key-2024",
            token_vault_key="c3VwZXItc2VjdXJlLXZhdWx0LWtleS0zMmI=",
        )
        assert config.is_production

    def test_is_production_property(self) -> None:
        """is_production should return True only for production env."""
        dev = Settings(app_env="development")
        prod = Settings(
            app_env="production",
            secret_key="real-key",
            jwt_secret_key="real-jwt-key",
            token_vault_key="cmVhbC12YXVsdC1rZXktMzItYnl0ZXMtbG9uZw==",
        )
        assert not dev.is_production
        assert prod.is_production
