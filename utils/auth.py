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
    """Render the login form with modern SaaS medical design"""
    from utils.colors import COLORS
    
    # Inject CSS for modern login design
    st.markdown(f"""
    <style>
    /* Hide default Streamlit UI elements */
    [data-testid="stToolbar"] {{ display: none; }}
    
    /* Page background - soft medical blue gradient */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['background']} 0%, #E8F4F8 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    /* Login card container */
    .login-container {{
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
        padding: 40px;
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
    }}
    
    /* Branding section */
    .login-header {{
        margin-bottom: 30px;
    }}
    
    .login-title {{
        font-size: 32px;
        font-weight: 700;
        color: {COLORS['primary']};
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }}
    
    .login-subtitle {{
        font-size: 13px;
        color: {COLORS['text_light']};
        margin: 0;
        font-weight: 400;
    }}
    
    /* Form styling */
    .login-form {{
        margin-top: 30px;
    }}
    
    /* Input field styling */
    .login-form input[type="text"],
    .login-form input[type="password"] {{
        width: 100% !important;
        padding: 12px 14px !important;
        margin-bottom: 14px !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        box-sizing: border-box !important;
    }}
    
    .login-form input[type="text"]:focus,
    .login-form input[type="password"]:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px {COLORS['primary']}15 !important;
        outline: none !important;
    }}
    
    /* Submit button styling */
    .login-button {{
        width: 100% !important;
        padding: 12px 16px !important;
        background: {COLORS['primary']} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        margin-top: 8px !important;
        transition: all 0.2s ease !important;
    }}
    
    .login-button:hover {{
        background: {COLORS['primary_dark']} !important;
        box-shadow: 0 4px 12px {COLORS['primary']}40 !important;
    }}
    
    .login-button:active {{
        transform: translateY(1px) !important;
    }}
    
    /* Error and success messages */
    .stAlert {{
        border-radius: 6px !important;
        border-left: 4px solid !important;
    }}
    
    /* Demo users expander */
    .demo-credentials {{
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #E0E0E0;
    }}
    
    .demo-credentials details {{
        cursor: pointer;
    }}
    
    .demo-credentials summary {{
        color: {COLORS['text_light']};
        font-size: 12px;
        font-weight: 500;
        outline: none;
    }}
    
    .demo-credentials summary:hover {{
        color: {COLORS['primary']};
    }}
    
    .demo-code {{
        background: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 12px;
        margin-top: 12px;
        font-size: 11px;
        text-align: left;
        font-family: 'Monaco', 'Courier New', monospace;
    }}
    
    /* Override form container width */
    .stForm {{
        max-width: 100% !important;
    }}
    
    div[data-testid="stForm"] {{
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }}
    
    /* Center content vertically */
    .block-container {{
        padding-top: 40px;
        padding-bottom: 40px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Wrapper container for centering
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # Login card container
        st.markdown(f"""
        <div class="login-container">
            <div class="login-header">
                <div class="login-title">🔐 CogniData</div>
                <div class="login-subtitle">Evaluación Neuropsicológica</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", border=False):
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            
            username = st.text_input(
                "Usuario",
                placeholder="usuario@clinica.com",
                label_visibility="collapsed"
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Contraseña segura",
                label_visibility="collapsed"
            )
            
            # Custom button with better styling
            col_btn1, col_btn2, col_btn3 = st.columns([0.5, 3, 0.5])
            with col_btn2:
                submitted = st.form_submit_button(
                    "🔓 Iniciar Sesión",
                    use_container_width=True,
                    type="primary"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submitted:
                if login(username, password):
                    st.success(f"✅ ¡Bienvenido, {st.session_state.user.full_name}!")
                    st.rerun()
                else:
                    attempts = st.session_state.login_attempts
                    st.error(f"❌ Credenciales inválidas. Intento {attempts}/5")
                    
                    if attempts >= 5:
                        st.warning("⏱️ Demasiados intentos. Por favor, espera un momento.")
        
        # Demo credentials in expandable section
        st.markdown("""
        <div class="demo-credentials">
        <details>
        <summary>📝 Usuarios de prueba disponibles</summary>
        <div class="demo-code">
admin / admin123<br>
clinician / clinical123<br>
viewer / viewer123
        </div>
        </details>
        </div>
        """, unsafe_allow_html=True)


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
