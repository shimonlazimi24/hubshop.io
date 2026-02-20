import hashlib
import hmac

from backend.config import settings


def verify_shop_webhook(body: bytes, authorization_header: str) -> bool:
    """Verify TikTok Shop webhook signature.

    Signature = HMAC-SHA256(app_secret, app_key + body)
    """
    expected = hmac.new(
        settings.tiktok_shop_app_secret.encode("utf-8"),
        (settings.tiktok_shop_app_key + body.decode("utf-8")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, authorization_header)


def verify_developer_webhook(body: bytes, signature_header: str) -> bool:
    """Verify TikTok Developer webhook signature.

    Header format: t=<timestamp>,s=<signature>
    Signature = HMAC-SHA256(client_secret, <timestamp>.<body>)
    """
    parts: dict[str, str] = {}
    for segment in signature_header.split(","):
        key, _, value = segment.partition("=")
        parts[key.strip()] = value.strip()

    timestamp = parts.get("t", "")
    provided_sig = parts.get("s", "")

    if not timestamp or not provided_sig:
        return False

    expected = hmac.new(
        settings.tiktok_developer_client_secret.encode("utf-8"),
        f"{timestamp}.{body.decode('utf-8')}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, provided_sig)
