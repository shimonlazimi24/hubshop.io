from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, status

from backend.db.models.organization import Role

# Role hierarchy: higher index = more permissions
_ROLE_HIERARCHY: dict[Role, int] = {
    Role.VIEWER: 0,
    Role.MEMBER: 1,
    Role.MANAGER: 2,
    Role.ADMIN: 3,
    Role.OWNER: 4,
}


def has_permission(user_role: Role, required_role: Role) -> bool:
    """Check if user_role has at least the permissions of required_role."""
    return _ROLE_HIERARCHY.get(user_role, -1) >= _ROLE_HIERARCHY.get(required_role, 999)


def require_role(minimum_role: Role) -> Callable:
    """Dependency factory that checks the current user's role against a minimum required role."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_user = kwargs.get("current_user")
            membership = kwargs.get("membership")
            if not current_user or not membership:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authentication context missing",
                )
            if not has_permission(membership.role, minimum_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires at least {minimum_role.value} role",
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
