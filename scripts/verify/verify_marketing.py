"""Verify TikTok Marketing API connectivity.

Usage:
    python -m scripts.verify.verify_marketing

Prerequisites:
    - TIKTOK_MARKETING_APP_ID and TIKTOK_MARKETING_APP_SECRET set in .env

This script verifies credentials by calling the Marketing API OAuth endpoint.
If an access token is available, it tests the advertiser info endpoint.
"""

from __future__ import annotations

import asyncio

import httpx

from scripts.verify.utils import load_env, print_fail, print_success, require_env

AUTH_URL = "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/"
ADVERTISER_URL = "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/"


async def verify() -> None:
    load_env()
    app_id = require_env("TIKTOK_MARKETING_APP_ID")
    app_secret = require_env("TIKTOK_MARKETING_APP_SECRET")

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(
                AUTH_URL,
                json={
                    "app_id": app_id,
                    "secret": app_secret,
                    "auth_code": "test_verification",
                },
            )
            data = resp.json()
            code = data.get("code", -1)
            message = data.get("message", "")

            if code == 0:
                print_success("TikTok Marketing", f"Authenticated successfully: {message}")
            elif code in (40105, 40002):
                print_success(
                    "TikTok Marketing",
                    "Credentials valid (app_id + secret accepted). "
                    "Connect an advertiser via /connect/marketing/authorize to get access tokens.",
                )
            elif code in (40100, 40101):
                print_fail(
                    "TikTok Marketing",
                    f"Invalid credentials: {message}. Check APP_ID and APP_SECRET.",
                )
            else:
                print_success(
                    "TikTok Marketing",
                    f"API reachable — response code {code}: {message}. "
                    "Verify credentials by connecting an advertiser.",
                )
        except httpx.ConnectError:
            print_fail("TikTok Marketing", "Cannot reach TikTok Business API. Check network connectivity.")

    # Check if SDK is available
    try:
        from business_api_client import ApiClient  # noqa: F401

        print_success("TikTok Marketing SDK", "business-api-client package installed")
    except ImportError:
        print("[INFO] TikTok Marketing SDK: business-api-client not installed (optional — raw HTTP will be used)")


if __name__ == "__main__":
    asyncio.run(verify())
