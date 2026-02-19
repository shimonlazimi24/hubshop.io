import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from backend.config import settings

_NONCE_SIZE = 12  # 96-bit nonce for AES-GCM


def _get_key() -> bytes:
    return base64.b64decode(settings.token_vault_key)


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token string using AES-256-GCM. Returns base64(nonce + ciphertext)."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt_token(encrypted: str) -> str:
    """Decrypt a base64(nonce + ciphertext) token using AES-256-GCM."""
    key = _get_key()
    aesgcm = AESGCM(key)
    raw = base64.b64decode(encrypted)
    nonce = raw[:_NONCE_SIZE]
    ciphertext = raw[_NONCE_SIZE:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
