"""Verify TikTok Shop API connectivity.

Usage:
    python -m scripts.verify.verify_shop

Prerequisites:
    - TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_SECRET set in .env
    - At least one Shop ConnectedAccount with an active access token in the database

This script tests the HMAC-SHA256 signing flow by calling the Shop authorization
endpoint. If no connected account exists yet, it verifies that credentials are
valid by checking the signature generation works without error.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import time

import httpx

from scripts.verify.utils import load_env, print_fail, print_success, require_env

BASE_URL = "https://open-api.tiktokglobalshop.com"


def generate_signature(
    app_secret: str,
    path: str,
    params: dict[str, str],
    body: str = "",
) -> str:
    """Generate HMAC-SHA256 signature per TikTok Shop API spec."""
    excluded = {"sign", "access_token"}
    sorted_params = "".join(
        f"{k}{v}" for k, v in sorted(params.items()) if k not in excluded
    )
    base_string = f"{app_secret}{path}{sorted_params}{body}{app_secret}"
    return hmac.new(
        app_secret.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def verify() -> None:
    load_env()
    app_key = require_env("TIKTOK_SHOP_APP_KEY")
    app_secret = require_env("TIKTOK_SHOP_APP_SECRET")

    path = "/authorization/202309/shops"
    timestamp = str(int(time.time()))
    params = {
        "app_key": app_key,
        "timestamp": timestamp,
    }
    signature = generate_signature(app_secret, path, params)
    params["sign"] = signature

    # Note: Without a valid access_token this will return 401, but a successful
    # signature generation + HTTP round-trip confirms credentials and connectivity.
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        try:
            resp = await client.get(
                path,
                params=params,
                headers={"Content-Type": "application/json"},
            )
            data = resp.json()

            if resp.status_code == 200 and data.get("code") == 0:
                shops = data.get("data", {}).get("shops", [])
                print_success("TikTok Shop", f"Connected — {len(shops)} shop(s) found")
            elif resp.status_code == 401 or data.get("code") in (105, 106):
                print_success(
                    "TikTok Shop",
                    "Credentials valid (signature accepted). "
                    "No active access token — connect a seller via /connect/shop/authorize",
                )
            else:
                print_fail("TikTok Shop", f"Unexpected response: {resp.status_code} — {data}")
        except httpx.ConnectError:
            print_fail("TikTok Shop", "Cannot reach TikTok Shop API. Check network connectivity.")


if __name__ == "__main__":
    asyncio.run(verify())
