"""Tests for password validation and async password hashing (backend/auth/passwords.py)."""

import pytest
from fastapi import HTTPException

from backend.auth.passwords import (
    hash_password,
    hash_password_async,
    validate_password,
    verify_password_async,
)


@pytest.mark.unit
class TestValidatePassword:
    """Tests for the validate_password policy enforcement."""

    def test_password_too_short_raises_400(self) -> None:
        """Passwords shorter than 8 characters should be rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("Ab1")
        assert exc_info.value.status_code == 400

    def test_password_exactly_min_length_without_requirements_raises_400(self) -> None:
        """8-char password without all character classes should be rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("abcdefgh")  # no uppercase, no digit
        assert exc_info.value.status_code == 400

    def test_password_without_uppercase_raises_400(self) -> None:
        """Password without uppercase letter should be rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("abcdefg1")
        assert exc_info.value.status_code == 400

    def test_password_without_lowercase_raises_400(self) -> None:
        """Password without lowercase letter should be rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("ABCDEFG1")
        assert exc_info.value.status_code == 400

    def test_password_without_digit_raises_400(self) -> None:
        """Password without digit should be rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("Abcdefgh")
        assert exc_info.value.status_code == 400

    def test_valid_password_passes(self) -> None:
        """Password meeting all requirements should pass without exception."""
        validate_password("SecureP1")  # 8 chars, upper, lower, digit

    def test_strong_password_passes(self) -> None:
        """Strong password with special characters should pass."""
        validate_password("MyP@ssw0rd!2024")

    def test_empty_password_raises_400(self) -> None:
        """Empty string should be rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("")
        assert exc_info.value.status_code == 400

    def test_error_detail_contains_requirements(self) -> None:
        """Error message should describe the password requirements."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("weak")
        assert "uppercase" in exc_info.value.detail.lower()
        assert "digit" in exc_info.value.detail.lower()


@pytest.mark.unit
class TestAsyncPasswordHashing:
    """Tests for the async password hashing and verification helpers."""

    async def test_hash_password_async_returns_hash(self) -> None:
        """hash_password_async should return a bcrypt hash different from the input."""
        hashed = await hash_password_async("TestPassword1")
        assert hashed != "TestPassword1"
        assert hashed.startswith("$2b$")  # bcrypt prefix

    async def test_verify_password_async_correct(self) -> None:
        """verify_password_async should return True for matching password."""
        password = "CorrectPass1"
        hashed = hash_password(password)
        result = await verify_password_async(password, hashed)
        assert result is True

    async def test_verify_password_async_incorrect(self) -> None:
        """verify_password_async should return False for wrong password."""
        hashed = hash_password("OriginalPass1")
        result = await verify_password_async("WrongPass1", hashed)
        assert result is False

    async def test_hash_password_async_unique_salts(self) -> None:
        """Two hashes of the same password should differ (unique salt)."""
        h1 = await hash_password_async("SamePass1")
        h2 = await hash_password_async("SamePass1")
        assert h1 != h2
