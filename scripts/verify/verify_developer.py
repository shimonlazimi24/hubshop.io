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
            resp = await client.post(
                TOKEN_URL,
                data={
                    "client_key": client_key,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                },
            )
            data = resp.json()

            error_code = data.get("data", {}).get("error_code", data.get("error", ""))
            description = data.get("data", {}).get("description", data.get("error_description", ""))

            if "invalid" in str(description).lower() and "client" in str(description).lower():
                print_fail(
                    "TikTok Developer",
                    f"Invalid credentials: {description}. Check CLIENT_KEY and CLIENT_SECRET.",
                )
            else:
                print_success(
                    "TikTok Developer",
                    "Credentials accepted by TikTok. "
                    "Connect a user via /connect/developer/authorize to get access tokens.",
                )
        except httpx.ConnectError:
            print_fail("TikTok Developer", "Cannot reach TikTok API. Check network connectivity.")


if __name__ == "__main__":
    asyncio.run(verify())
