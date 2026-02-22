"""Run all platform verification scripts and report results.

Usage:
    python -m scripts.verify.verify_all
"""

from __future__ import annotations

import subprocess
import sys

SCRIPTS = [
    "scripts.verify.verify_shop",
    "scripts.verify.verify_developer",
    "scripts.verify.verify_marketing",
    "scripts.verify.verify_research",
    "scripts.verify.verify_live",
]


def main() -> None:
    print("=" * 60)
    print("Frodo Platform Verification Suite")
    print("=" * 60)
    print()

    results: list[tuple[str, bool]] = []

    for script in SCRIPTS:
        platform = script.split("_")[-1].capitalize()
        print(f"--- {platform} ---")
        result = subprocess.run(
            [sys.executable, "-m", script],
            capture_output=False,
        )
        passed = result.returncode == 0
        results.append((platform, passed))
        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    for platform, passed in results:
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {platform}")

    failed = [p for p, ok in results if not ok]
    if failed:
        print(f"\n{len(failed)} platform(s) failed. See output above for details.")
        sys.exit(1)
    else:
        print(f"\nAll {len(results)} platforms verified successfully.")


if __name__ == "__main__":
    main()
