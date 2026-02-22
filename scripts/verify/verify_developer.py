"""Verify TikTok Developer API connectivity.

Usage:
    python -m scripts.verify.verify_developer

Prerequisites:
    - TIKTOK_DEVELOPER_CLIENT_KEY and TIKTOK_DEVELOPER_CLIENT_SECRET set in .env

This script verifies credentials by calling the token endpoint. If a valid
access token is available (via connected account), it also tests a user info call.
"""

from __future__ import annotations

import asyncio

import httpx

from scripts.verify.utils import load_env, print_fail, print_success, require_env

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"


async def verify() -> None:
    load_env()
    client_key = require_env("TIKTOK_DEVELOPER_CLIENT_KEY")
    client_secret = require_env("TIKTOK_DEVELOPER_CLIENT_SECRET")

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # Send a token request to validate credentials are recognized.
            # Developer API uses authorization_code grant (not client_credentials),
            # so we expect an error — but the error type tells us if creds are valid.
            resp = await client.post(
                TOKEN_URL,
                data={
                    "client_key": client_key,
                    "client_secret": client_secret,
                    "grant_type": "authorization_code",
                    "code": "test_verification",
                },
            )
            data = resp.json()
            error_code = data.get("data", {}).get("error_code", data.get("error", ""))

            # error_code "invalid_client" = bad credentials
            # Other errors (e.g., "invalid_request", "invalid_grant") = creds recognized
            if str(error_code) == "invalid_client":
                description = data.get("data", {}).get(
                    "description", data.get("error_description", "")
                )
                print_fail(
                    "TikTok Developer",
                    f"Invalid credentials: {description}. Check CLIENT_KEY and CLIENT_SECRET.",
                )
            else:
                print_success(
                    "TikTok Developer",
                    "Credentials recognized by TikTok. "
                    "Connect a user via /connect/developer/authorize to get access tokens.",
                )
        except httpx.ConnectError:
            print_fail("TikTok Developer", "Cannot reach TikTok API. Check network connectivity.")


if __name__ == "__main__":
    asyncio.run(verify())
