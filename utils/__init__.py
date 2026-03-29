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

from utils.alerts import (
    modal_success,
    modal_error,
    modal_warning,
    modal_info,
    toast_success,
    toast_error,
    toast_warning,
    toast_info,
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
    "modal_success",
    "modal_error",
    "modal_warning",
    "modal_info",
    "toast_success",
    "toast_error",
    "toast_warning",
    "toast_info",
]
