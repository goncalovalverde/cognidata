"""
Authentication module for CogniData
Provides session-based authentication and role-based access control
"""

import streamlit as st
import hashlib
import os
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

from services.audit import audit_service


@dataclass
class User:
    """User model for authentication"""

    username: str
    role: str
    full_name: str = ""
    created_at: datetime = None


class Role:
    ADMIN = "admin"
    CLINICIAN = "clinician"
    VIEWER = "viewer"

    ALL = [ADMIN, CLINICIAN, VIEWER]


class AuthService:
    """
    Authentication service with role-based access control.

    Default users (for demo purposes - in production, use proper user management):
    - admin/admin123 (full access)
    - clinician/clinical123 (can create tests, view reports)
    - viewer/viewer123 (read-only access)
    """

    def __init__(self):
        self._users = self._load_users()

    def _load_users(self) -> dict:
        """
        Load users from environment variables or use defaults.
        In production, this should load from a database.
        """
        users = {}

        default_users = {
            "admin": {
                "password": "admin123",
                "role": Role.ADMIN,
                "full_name": "Administrador",
            },
            "clinician": {
                "password": "clinical123",
                "role": Role.CLINICIAN,
                "full_name": " Clínico",
            },
            "viewer": {
                "password": "viewer123",
                "role": Role.VIEWER,
                "full_name": "Observador",
            },
        }

        for username, data in default_users.items():
            env_password = os.getenv(f"AUTH_{username.upper()}_PASSWORD")
            if env_password:
                data["password"] = env_password
            users[username] = data

        return users

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.

        Args:
            username: The username
            password: The plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        if username not in self._users:
            return None

        user_data = self._users[username]
        password_hash = self._hash_password(password)

        expected_hash = self._hash_password(user_data["password"])

        if password_hash != expected_hash:
            return None

        return User(
            username=username,
            role=user_data["role"],
            full_name=user_data.get("full_name", username),
            created_at=datetime.utcnow(),
        )

    def has_permission(self, user: User, required_role: str) -> bool:
        """
        Check if user has the required role or higher.

        Role hierarchy:
        admin > clinician > viewer
        """
        role_hierarchy = {
            Role.VIEWER: 0,
            Role.CLINICIAN: 1,
            Role.ADMIN: 2,
        }

        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def can_delete(self, user: User) -> bool:
        """Check if user can delete data"""
        return user.role == Role.ADMIN

    def can_create_test(self, user: User) -> bool:
        """Check if user can create tests"""
        return user.role in [Role.ADMIN, Role.CLINICIAN]

    def can_view_reports(self, user: User) -> bool:
        """Check if user can view reports"""
        return user.role in [Role.ADMIN, Role.CLINICIAN, Role.VIEWER]


auth_service = AuthService()


def init_auth_state():
    """Initialize authentication state in Streamlit session state"""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0


def require_auth():
    """
    Decorator/guard to require authentication.
    If not authenticated, shows login form and stops execution.
    """
    init_auth_state()

    if not st.session_state.authenticated:
        _render_login_form()
        st.stop()


def require_role(required_role: str):
    """
    Guard to require a specific role.
    Shows access denied if user doesn't have required role.
    """
    require_auth()

    user = st.session_state.user
    if not auth_service.has_permission(user, required_role):
        st.error("⛔ No tienes permisos para acceder a esta función")
        st.stop()


def login(username: str, password: str) -> bool:
    """
    Attempt to log in a user.

    Returns:
        True if login successful, False otherwise
    """
    user = auth_service.authenticate(username, password)

    if user:
        st.session_state.user = user
        st.session_state.authenticated = True
        st.session_state.login_attempts = 0
        audit_service.log(
            action="auth.login",
            resource_type="system",
            details={"username": username, "role": user.role},
        )
        return True

    st.session_state.login_attempts += 1
    return False


def logout():
    """Log out the current user"""
    if st.session_state.get("user"):
        audit_service.log(
            action="auth.logout",
            resource_type="system",
            details={"username": st.session_state.user.username},
        )

    st.session_state.user = None
    st.session_state.authenticated = False


def get_current_user() -> Optional[User]:
    """Get the currently authenticated user"""
    return st.session_state.get("user")


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)


def _render_login_form():
    """Render the login form"""
    st.title("🔐 CogniData - Iniciar Sesión")
    st.markdown("### Gestión de tests y cálculo de normas NEURONORMA")

    st.markdown("---")

    with st.form("login_form"):
        st.subheader("Credenciales de Acceso")

        username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input(
            "Contraseña", type="password", placeholder="Ingresa tu contraseña"
        )

        submitted = st.form_submit_button("Iniciar Sesión", type="primary")

        if submitted:
            if login(username, password):
                st.success(f"✅ Bienvenido, {st.session_state.user.full_name}!")
                st.rerun()
            else:
                attempts = st.session_state.login_attempts
                st.error(f"❌ Credenciales inválidas. Intento {attempts}/5")

                if attempts >= 5:
                    st.warning("Demasiados intentos. Por favor, espera un momento.")

    st.markdown("---")
    st.markdown("**Usuarios de demostración:**")
    st.code("""
    admin / admin123     - Administrador (acceso total)
    clinician / clinical123 - Clínico (crear tests, ver reportes)  
    viewer / viewer123   - Observador (solo lectura)
    """)


def render_user_menu():
    """Render user info and logout button in sidebar"""
    if is_authenticated():
        user = get_current_user()

        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 {user.full_name}**")
        st.sidebar.caption(f"Rol: {user.role.capitalize()}")

        if st.sidebar.button("Cerrar Sesión", key="logout_btn"):
            logout()
            st.rerun()
