import pytest

from backend.auth.passwords import hash_password, verify_password


@pytest.mark.unit
class TestPasswords:
    def test_hash_and_verify(self) -> None:
        password = "secure-password-123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self) -> None:
        hashed = hash_password("correct-password")
        assert not verify_password("wrong-password", hashed)

    def test_different_hashes_for_same_password(self) -> None:
        password = "same-password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # bcrypt salt ensures uniqueness
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
