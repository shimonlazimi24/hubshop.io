"""Verify TikTok LIVE integration readiness.

Usage:
    python -m scripts.verify.verify_live

Prerequisites:
    - TikTokLive package installed: pip install TikTokLive

This script checks that the TikTokLive package is installed and the
Frodo wrapper can be instantiated. No credentials or network calls needed.
"""

from __future__ import annotations

from scripts.verify.utils import load_env, print_fail, print_success


def verify() -> None:
    load_env()

    # Check TikTokLive package
    try:
        import TikTokLive  # noqa: F401

        print_success("TikTok LIVE", "TikTokLive package installed")
    except ImportError:
        print_fail(
            "TikTok LIVE",
            "TikTokLive package not installed. Run: pip install TikTokLive",
        )
        return

    # Check Frodo wrapper
    try:
        from backend.tiktok.live.client import LiveEventType, TikTokLiveClientWrapper

        wrapper = TikTokLiveClientWrapper(unique_id="test_user")
        assert wrapper is not None
        assert len(LiveEventType) == 7
        print_success("TikTok LIVE", "Frodo wrapper instantiated — 7 event types registered")
    except NotImplementedError:
        print_fail(
            "TikTok LIVE",
            "Wrapper raised NotImplementedError — check TikTokLive installation",
        )
    except Exception as e:
        print_fail("TikTok LIVE", f"Wrapper error: {e}")


if __name__ == "__main__":
    verify()
