"""
Authentication module for CogniData
Provides session-based authentication, role-based access control, and JWT-based session persistence
Uses database-backed user authentication with bcrypt password hashing
"""

import streamlit as st
import bcrypt
import os
import sys
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

from services.audit import audit_service
from utils.jwt_manager import JWTManager
from database.connection import SessionLocal
from models.user import User as DBUser, UserRole


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
    All users are stored in the database with bcrypt-hashed passwords.
    """

    def __init__(self):
        pass  # Defer admin initialization to first authenticate call

    def _ensure_admin_exists(self):
        """
        Ensure at least one admin user exists.
        Called lazily on first authentication attempt to avoid
        import-time database access.
        
        CRITICAL: Admin password MUST be provided via ADMIN_PASSWORD environment variable.
        This prevents default credentials vulnerability (GDPR Article 32).
        """
        db = SessionLocal()
        try:
            admin_count = db.query(DBUser).filter(DBUser.role == UserRole.ADMIN).count()
            if admin_count == 0:
                # CRITICAL FIX: Require ADMIN_PASSWORD environment variable
                admin_password = os.getenv("ADMIN_PASSWORD")
                if not admin_password:
                    print(
                        "FATAL: ADMIN_PASSWORD environment variable is not set\n"
                        "CogniData requires a secure admin password to be set before first use.\n\n"
                        "Set a strong password (12+ chars, mixed case, numbers, special chars):\n"
                        "  export ADMIN_PASSWORD='your_secure_password'\n\n"
                        "Then restart the application.\n\n"
                        "For production, store this in a secure vault (AWS Secrets Manager, Azure Key Vault, etc.)",
                        file=sys.stderr
                    )
                    sys.exit(1)
                
                admin_hash = self._hash_password(admin_password)
                
                admin = DBUser(
                    username="admin",
                    password_hash=admin_hash,
                    full_name="Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                db.add(admin)
                db.commit()
        except Exception as e:
            # Silently fail if table doesn't exist yet (will be created on init_db)
            pass
        finally:
            db.close()

    def _init_default_admin(self):
        """
        Ensure at least one admin user exists.
        Called on startup to initialize database if empty.
        
        CRITICAL: Admin password MUST be provided via ADMIN_PASSWORD environment variable.
        This prevents default credentials vulnerability (GDPR Article 32).
        """
        db = SessionLocal()
        try:
            admin_count = db.query(DBUser).filter(DBUser.role == UserRole.ADMIN).count()
            if admin_count == 0:
                # CRITICAL FIX: Require ADMIN_PASSWORD environment variable
                admin_password = os.getenv("ADMIN_PASSWORD")
                if not admin_password:
                    print(
                        "FATAL: ADMIN_PASSWORD environment variable is not set\n"
                        "CogniData requires a secure admin password to be set before first use.\n\n"
                        "Set a strong password (12+ chars, mixed case, numbers, special chars):\n"
                        "  export ADMIN_PASSWORD='your_secure_password'\n\n"
                        "Then restart the application.\n\n"
                        "For production, store this in a secure vault (AWS Secrets Manager, Azure Key Vault, etc.)",
                        file=sys.stderr
                    )
                    sys.exit(1)
                
                admin_hash = self._hash_password(admin_password)
                
                admin = DBUser(
                    username="admin",
                    password_hash=admin_hash,
                    full_name="Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                db.add(admin)
                db.commit()
        finally:
            db.close()

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password from database.

        Args:
            username: The username
            password: The plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Ensure admin user exists on first authentication attempt
        # (deferred from __init__ to avoid issues with table creation)
        self._ensure_admin_exists()
        
        db = SessionLocal()
        try:
            db_user = db.query(DBUser).filter(
                DBUser.username == username,
                DBUser.is_active == True
            ).first()

            if not db_user:
                return None

            if not self._verify_password(password, db_user.password_hash):
                return None

            # Map database role to internal role name
            role_map = {
                "Admin": "admin",
                "Practitioner": "clinician",
                "Viewer": "viewer",
            }
            internal_role = role_map.get(db_user.role.value, db_user.role.value)

            return User(
                username=db_user.username,
                role=internal_role,
                full_name=db_user.full_name or db_user.username,
                created_at=db_user.created_at,
            )
        finally:
            db.close()

    def has_permission(self, user: User, required_role: str) -> bool:
        """
        Check if user has the required role or higher.

        Role hierarchy:
        admin > clinician > viewer
        """
        # Map database role names to internal role names
        role_map = {
            "Admin": "admin",
            "Practitioner": "clinician",
            "Viewer": "viewer",
            "admin": "admin",
            "clinician": "clinician",
            "viewer": "viewer",
        }
        
        role_hierarchy = {
            "viewer": 0,
            "clinician": 1,
            "admin": 2,
        }

        user_role = role_map.get(user.role, user.role)
        required_role_mapped = role_map.get(required_role, required_role)
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role_mapped, 0)

        return user_level >= required_level

    def can_delete(self, user: User) -> bool:
        """Check if user can delete data"""
        return user.role.lower() == Role.ADMIN.lower()

    def can_create_test(self, user: User) -> bool:
        """Check if user can create tests"""
        user_role = user.role.lower()
        return user_role in [Role.ADMIN.lower(), Role.CLINICIAN.lower()]

    def can_view_reports(self, user: User) -> bool:
        """Check if user can view reports"""
        return True  # All authenticated users can view reports


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


def require_auth_with_persistence():
    """
    Require authentication with session persistence via database + secure session ID.
    
    CRITICAL FIX: session_id is stored in URL query parameter to survive page reloads.
    The actual JWT token remains server-side only.
    
    This prevents token exposure in:
    - Browser history (no token, just session_id)
    - Server access logs (no token)
    - Referer headers (no token)
    - Browser autocomplete (no token)
    
    Checks authentication in this order:
    1. st.session_state.authenticated (in-memory session from current run)
    2. URL query parameter session_id (survives page reloads)
    3. Database session record (validate session_id)
    4. Shows login form if none exist
    """
    from services.session_manager import SessionManager
    
    init_auth_state()
    
    # Already authenticated in memory (current page run)
    if st.session_state.authenticated:
        return
    
    # Try to get session_id from multiple sources
    session_id = st.session_state.get("session_id")
    
    # If not in session state, try to get from URL query parameter
    # This allows session to survive page reloads (F5, browser reload)
    if not session_id:
        from streamlit import query_params
        session_id = query_params.get("session_id", None)
        if isinstance(session_id, list):
            session_id = session_id[0]  # Handle list response from query_params
    
    # Try to restore session from database using session_id
    if session_id:
        session_record = SessionManager.get_session_by_id(session_id)
        if session_record:
            # session_record is a dict (from database query)
            # Check if session is valid and active
            is_active = session_record.get("is_active", False)
            token_expires_at = session_record.get("token_expires_at")
            
            # Check expiration
            is_expired = token_expires_at and datetime.utcnow() > token_expires_at
            
            if is_active and not is_expired:
                # Valid session found in database - restore it
                user = User(
                    username=session_record.get("username", ""),
                    role=session_record.get("role", "viewer"),
                    full_name=session_record.get("full_name", "")
                )
                st.session_state.user = user
                st.session_state.authenticated = True
                st.session_state.session_id = session_id
                return
    
    # No valid session - show login form
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
    
    CRITICAL FIX: JWT tokens are NO LONGER stored in URL query parameters.
    Instead, session_id is stored in URL as query parameter (safe to expose).
    The actual JWT token is kept server-side only.
    
    This prevents token exposure via browser history, logs, etc.
    Session persists across page reloads via URL query parameter.

    Returns:
        True if login successful, False otherwise
    """
    from services.session_manager import SessionManager
    from datetime import timedelta
    
    user = auth_service.authenticate(username, password)

    if user:
        st.session_state.user = user
        st.session_state.authenticated = True
        st.session_state.login_attempts = 0
        
        # Generate JWT token (kept server-side only, NOT in URL)
        token = JWTManager.generate_token(user)
        
        # Create database session record with session_id
        token_expires_at = datetime.utcnow() + timedelta(hours=JWTManager.EXPIRATION_HOURS)
        session_record = SessionManager.create_session(
            user=user,
            token=token,
            token_expires_at=token_expires_at,
        )
        
        # Store session_id in both session state and URL query parameter
        # URL parameter allows session to survive page reloads
        session_id = session_record.session_id
        st.session_state.session_id = session_id
        
        # Add session_id to URL query parameter for persistence across reloads
        from streamlit import query_params
        query_params["session_id"] = session_id
        
        audit_service.log(
            action="auth.login",
            resource_type="system",
            details={"username": username, "role": user.role},
        )
        return True

    st.session_state.login_attempts += 1
    
    # Log failed authentication attempt
    audit_service.log(
        action="auth.login_failed",
        resource_type="system",
        details={
            "username": username,
            "attempt_number": st.session_state.login_attempts,
            "reason": "invalid_credentials"
        },
    )
    
    return False


def logout():
    """Log out the current user and invalidate session"""
    from services.session_manager import SessionManager
    
    if st.session_state.get("user"):
        audit_service.log(
            action="auth.logout",
            resource_type="system",
            details={"username": st.session_state.user.username},
        )
        
        # Invalidate database session using session_id (NOT token)
        session_id = st.session_state.get("session_id")
        if session_id:
            SessionManager.invalidate_session_by_id(session_id)

    st.session_state.user = None
    st.session_state.authenticated = False
    st.session_state.session_id = None
    
    # Remove session_id from URL query parameter
    from streamlit import query_params
    if "session_id" in query_params:
        del query_params["session_id"]
    
    # Clean up old auth_token if it exists (legacy)
    if "auth_token" in st.session_state:
        del st.session_state["auth_token"]
    
    # Remove token from URL query parameters (legacy cleanup)
    if "auth_token" in st.query_params:
        del st.query_params["auth_token"]


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
