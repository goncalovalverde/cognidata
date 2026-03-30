"""
Server-side session model for persistent authentication.

Stores active JWT sessions in the database, allowing token recovery
across page reloads without relying on browser cookies.
"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from uuid import uuid4

from database.connection import Base


class AuthSession(Base):
    """
    Server-side authentication session storage.
    
    Allows users to maintain authenticated sessions across browser reloads
    by storing valid JWT tokens in the database with expiration times.
    
    When a user logs in:
    1. JWT token is created (24h validity)
    2. Session record stored in DB with token + expiration
    3. Token sent to browser (in-memory, can be lost on reload)
    
    On page reload (no token in memory):
    1. Load all valid sessions for this browser/client
    2. If valid session exists, restore authentication
    3. If session expired or missing, show login form
    
    Session IDs are browser-session-specific (not per-user).
    Multiple devices/browsers = multiple sessions per user.
    
    Table: auth_sessions
    - session_id: UUID primary key (unique per browser)
    - username: username of authenticated user
    - token: JWT token (hashed for security)
    - token_expires_at: when token expires
    - created_at: when session was created
    - last_accessed_at: last time this session was used
    - is_active: whether session is still valid
    """
    
    __tablename__ = "auth_sessions"
    
    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(100), nullable=False, index=True)
    
    # Store token hash instead of plain token for security
    # Clients send token in header, we hash it and compare
    token_hash = Column(String(256), nullable=False, unique=True)
    
    # Token expiration time (matches JWT exp)
    token_expires_at = Column(DateTime, nullable=False)
    
    # Session tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Browser/client identification (for managing multiple sessions per user)
    client_id = Column(String(36), nullable=True, index=True)  # Browser fingerprint or ID
    user_agent = Column(String(500), nullable=True)  # Browser user-agent
    
    def __repr__(self):
        return f"<AuthSession session_id={self.session_id} username={self.username}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.token_expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid and active"""
        return self.is_active and not self.is_expired
    
    def refresh_access_time(self):
        """Update last_accessed_at to current time"""
        self.last_accessed_at = datetime.utcnow()
