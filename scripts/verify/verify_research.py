"""Verify TikTok Research API connectivity.

Usage:
    python -m scripts.verify.verify_research

Prerequisites:
    - TIKTOK_RESEARCH_CLIENT_KEY and TIKTOK_RESEARCH_CLIENT_SECRET set in .env
    - Research API access approved by TikTok
"""

from __future__ import annotations

import asyncio

import httpx

from scripts.verify.utils import load_env, print_fail, print_success, require_env

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
VIDEO_QUERY_URL = "https://open.tiktokapis.com/v2/research/video/query/"


async def verify() -> None:
    load_env()
    client_key = require_env("TIKTOK_RESEARCH_CLIENT_KEY")
    client_secret = require_env("TIKTOK_RESEARCH_CLIENT_SECRET")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Get client credentials token
        try:
            resp = await client.post(
                TOKEN_URL,
                json={
                    "client_key": client_key,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                },
            )
            data = resp.json()
            access_token = data.get("data", {}).get("access_token", "")

            if not access_token:
                error = data.get("data", {}).get("description", data.get("message", "unknown error"))
                print_fail("TikTok Research", f"Failed to get token: {error}")

            print_success("TikTok Research", "Client credentials token obtained")

        except httpx.ConnectError:
            print_fail("TikTok Research", "Cannot reach TikTok API. Check network connectivity.")
            return

        # Step 2: Test a video query
        try:
            resp = await client.post(
                VIDEO_QUERY_URL,
                json={
                    "query": {"and": [{"field_name": "keyword", "operation": "IN", "field_values": ["tiktok"]}]},
                    "max_count": 1,
                    "start_date": "20240101",
                    "end_date": "20240102",
                },
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            data = resp.json()
            videos = data.get("data", {}).get("videos", [])
            print_success("TikTok Research", f"Video query returned {len(videos)} result(s)")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print_success("TikTok Research", "Token works but rate limited (5 QPS). Try again shortly.")
            else:
                print_fail("TikTok Research", f"Video query failed: {e.response.status_code}")


if __name__ == "__main__":
    asyncio.run(verify())
