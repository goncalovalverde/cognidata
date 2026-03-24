"""
Utils module - Utility functions and helpers
"""

from utils.auth import (
    auth_service,
    require_auth,
    require_role,
    login,
    logout,
    get_current_user,
    is_authenticated,
    render_user_menu,
    init_auth_state,
    Role,
    User,
)

__all__ = [
    "auth_service",
    "require_auth",
    "require_role",
    "login",
    "logout",
    "get_current_user",
    "is_authenticated",
    "render_user_menu",
    "init_auth_state",
    "Role",
    "User",
]
