"""Shared utilities for platform verification scripts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    """Load .env file from project root."""
    root = Path(__file__).resolve().parent.parent.parent
    env_path = root / ".env"
    if not env_path.exists():
        print(f"ERROR: .env file not found at {env_path}")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)
    load_dotenv(env_path)


def require_env(key: str) -> str:
    """Get a required environment variable or exit with a helpful message."""
    value = os.environ.get(key, "")
    if not value:
        print(f"ERROR: {key} is not set in .env")
        print(f"Please add your {key} to the .env file.")
        sys.exit(1)
    return value


def print_success(platform: str, detail: str) -> None:
    """Print a green success message."""
    print(f"[OK] {platform}: {detail}")


def print_fail(platform: str, detail: str) -> None:
    """Print a red failure message."""
    print(f"[FAIL] {platform}: {detail}")
    sys.exit(1)
