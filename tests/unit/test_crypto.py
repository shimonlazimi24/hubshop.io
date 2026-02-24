import base64
import os

import pytest


@pytest.fixture(autouse=True)
def _set_vault_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a valid 32-byte AES key for tests."""
    key = os.urandom(32)
    monkeypatch.setenv("TOKEN_VAULT_KEY", base64.b64encode(key).decode())
    # Force settings reload
    from backend.config import Settings

    monkeypatch.setattr("backend.utils.crypto.settings", Settings())


@pytest.mark.unit
class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self) -> None:
        from backend.utils.crypto import decrypt_token, encrypt_token

        plaintext = "TTP_abc123_access_token"
        encrypted = encrypt_token(plaintext)
        assert encrypted != plaintext
        decrypted = decrypt_token(encrypted)
        assert decrypted == plaintext

    def test_different_ciphertexts_for_same_plaintext(self) -> None:
        """Each encryption should produce unique output due to random nonce."""
        from backend.utils.crypto import encrypt_token

        plaintext = "same-token-value"
        enc1 = encrypt_token(plaintext)
        enc2 = encrypt_token(plaintext)
        assert enc1 != enc2

    def test_decrypt_with_wrong_key_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from backend.utils.crypto import encrypt_token

        encrypted = encrypt_token("secret-token")

        # Change key
        new_key = os.urandom(32)
        monkeypatch.setenv("TOKEN_VAULT_KEY", base64.b64encode(new_key).decode())
        from backend.config import Settings

        monkeypatch.setattr("backend.utils.crypto.settings", Settings())

        from backend.utils.crypto import decrypt_token

        with pytest.raises(Exception):  # InvalidTag from cryptography
            decrypt_token(encrypted)

    def test_empty_string_token(self) -> None:
        from backend.utils.crypto import decrypt_token, encrypt_token

        encrypted = encrypt_token("")
        assert decrypt_token(encrypted) == ""

    def test_unicode_token(self) -> None:
        from backend.utils.crypto import decrypt_token, encrypt_token

        token = "token-with-unicode-\u00e9\u00e8\u00ea"
        encrypted = encrypt_token(token)
        assert decrypt_token(encrypted) == token
