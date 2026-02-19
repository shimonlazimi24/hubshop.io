import pytest

from backend.auth.rbac import has_permission
from backend.db.models.organization import Role


@pytest.mark.unit
class TestRBAC:
    def test_owner_has_all_permissions(self) -> None:
        for role in Role:
            assert has_permission(Role.OWNER, role)

    def test_viewer_only_has_viewer_permission(self) -> None:
        assert has_permission(Role.VIEWER, Role.VIEWER)
        assert not has_permission(Role.VIEWER, Role.MEMBER)
        assert not has_permission(Role.VIEWER, Role.MANAGER)
        assert not has_permission(Role.VIEWER, Role.ADMIN)
        assert not has_permission(Role.VIEWER, Role.OWNER)

    def test_admin_has_admin_and_below(self) -> None:
        assert has_permission(Role.ADMIN, Role.VIEWER)
        assert has_permission(Role.ADMIN, Role.MEMBER)
        assert has_permission(Role.ADMIN, Role.MANAGER)
        assert has_permission(Role.ADMIN, Role.ADMIN)
        assert not has_permission(Role.ADMIN, Role.OWNER)

    def test_manager_has_manager_and_below(self) -> None:
        assert has_permission(Role.MANAGER, Role.VIEWER)
        assert has_permission(Role.MANAGER, Role.MEMBER)
        assert has_permission(Role.MANAGER, Role.MANAGER)
        assert not has_permission(Role.MANAGER, Role.ADMIN)

    def test_role_hierarchy_is_transitive(self) -> None:
        """If A >= B and B >= C, then A >= C."""
        assert has_permission(Role.OWNER, Role.ADMIN)
        assert has_permission(Role.ADMIN, Role.MANAGER)
        assert has_permission(Role.OWNER, Role.MANAGER)
