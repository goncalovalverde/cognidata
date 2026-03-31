"""
Unit tests for authentication module
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from utils.auth import (
    AuthService,
    Role,
    User,
    auth_service,
    login,
    logout,
    get_current_user,
    is_authenticated,
)


@pytest.fixture(scope="function", autouse=True)
def setup_env_vars():
    """Setup required environment variables for tests"""
    # Set admin password from env or use test default
    if "ADMIN_PASSWORD" not in os.environ:
        os.environ["ADMIN_PASSWORD"] = "TestAdminPass123!"
    yield
    # Cleanup is handled by pytest


class TestAuthService:
    """Tests for AuthService class"""

    def test_authenticate_valid_admin(self):
        """Test authentication with valid admin credentials"""
        service = AuthService()
        # Use password from environment variable (or test default from fixture)
        admin_password = os.environ.get("ADMIN_PASSWORD", "TestAdminPass123!")
        user = service.authenticate("admin", admin_password)

        assert user is not None
        assert user.username == "admin"
        assert user.role == Role.ADMIN
        assert user.full_name == "Administrator"

    def test_authenticate_valid_clinician(self):
        """Test authentication with valid clinician credentials"""
        service = AuthService()
        user = service.authenticate("clinician", "clinical123")

        assert user is not None
        assert user.username == "clinician"
        assert user.role == Role.CLINICIAN

    def test_authenticate_valid_viewer(self):
        """Test authentication with valid viewer credentials"""
        service = AuthService()
        user = service.authenticate("viewer", "viewer123")

        assert user is not None
        assert user.username == "viewer"
        assert user.role == Role.VIEWER

    def test_authenticate_invalid_username(self):
        """Test authentication with invalid username"""
        service = AuthService()
        user = service.authenticate("nonexistent", "password")

        assert user is None

    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password"""
        service = AuthService()
        admin_password = os.environ.get("ADMIN_PASSWORD", "TestAdminPass123!")
        user = service.authenticate("admin", "wrongpassword")

        assert user is None

    def test_authenticate_empty_credentials(self):
        """Test authentication with empty credentials"""
        service = AuthService()
        user = service.authenticate("", "")

        assert user is None


class TestRolePermissions:
    """Tests for role-based permissions"""

    def test_admin_has_all_permissions(self):
        """Test that admin has all permissions"""
        service = AuthService()
        admin = User(username="admin", role=Role.ADMIN, full_name="Admin")

        assert service.has_permission(admin, Role.ADMIN)
        assert service.has_permission(admin, Role.CLINICIAN)
        assert service.has_permission(admin, Role.VIEWER)
        assert service.can_delete(admin)
        assert service.can_create_test(admin)
        assert service.can_view_reports(admin)

    def test_clinician_permissions(self):
        """Test clinician role permissions"""
        service = AuthService()
        clinician = User(
            username="clinician", role=Role.CLINICIAN, full_name="Clinician"
        )

        assert not service.has_permission(clinician, Role.ADMIN)
        assert service.has_permission(clinician, Role.CLINICIAN)
        assert service.has_permission(clinician, Role.VIEWER)
        assert not service.can_delete(clinician)
        assert service.can_create_test(clinician)
        assert service.can_view_reports(clinician)

    def test_viewer_permissions(self):
        """Test viewer role permissions"""
        service = AuthService()
        viewer = User(username="viewer", role=Role.VIEWER, full_name="Viewer")

        assert not viewer_has_admin_permission(service, viewer)
        assert not service.has_permission(viewer, Role.CLINICIAN)
        assert service.has_permission(viewer, Role.VIEWER)
        assert not service.can_delete(viewer)
        assert not service.can_create_test(viewer)
        assert service.can_view_reports(viewer)


def viewer_has_admin_permission(service, viewer):
    """Helper to check if viewer has admin permission"""
    return service.has_permission(viewer, Role.ADMIN)


class TestUserModel:
    """Tests for User dataclass"""

    def test_user_creation(self):
        """Test creating a user"""
        user = User(username="testuser", role=Role.CLINICIAN, full_name="Test User")

        assert user.username == "testuser"
        assert user.role == Role.CLINICIAN
        assert user.full_name == "Test User"

    def test_user_default_full_name(self):
        """Test user with default full name"""
        user = User(username="testuser", role=Role.VIEWER)

        assert user.full_name == ""


class TestRoleConstants:
    """Tests for Role constants"""

    def test_role_constants(self):
        """Test role constants are defined correctly"""
        assert Role.ADMIN == "admin"
        assert Role.CLINICIAN == "clinician"
        assert Role.VIEWER == "viewer"
        assert Role.ALL == [Role.ADMIN, Role.CLINICIAN, Role.VIEWER]
