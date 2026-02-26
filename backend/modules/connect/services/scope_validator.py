"""Validate granted OAuth scopes against required scopes per platform."""

from __future__ import annotations

REQUIRED_SCOPES: dict[str, list[str]] = {
    "developer": [
        "user.info.basic",
        "user.info.profile",
        "user.info.stats",
        "video.list",
        "video.publish",
        "video.upload",
        "comment.list",
        "comment.list.manage",
    ],
    # Shop and Marketing use implicit scopes (controlled at TikTok portal level)
}


def validate_scopes(platform: str, granted_scopes: str | None) -> dict:
    """Compare granted scopes against required scopes for a platform.

    Returns dict with 'valid' bool and 'missing' list of scope strings.
    """
    required = REQUIRED_SCOPES.get(platform)
    if not required:
        return {"valid": True, "missing": []}

    if not granted_scopes:
        return {"valid": False, "missing": required}

    granted_set = {s.strip() for s in granted_scopes.split(",") if s.strip()}
    missing = [s for s in required if s not in granted_set]
    return {"valid": len(missing) == 0, "missing": missing}
