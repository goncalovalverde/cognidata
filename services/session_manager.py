"""
Session Management Service

Handles server-side session storage, validation, and cleanup.
Enables JWT token persistence across page reloads.
"""

import hashlib
from datetime import datetime
from typing import Optional
import uuid

from database.connection import SessionLocal
from models.session import AuthSession
from utils.auth import User
from utils.jwt_manager import JWTManager


class SessionManager:
    """
    Manages server-side authentication sessions.
    
    Flow:
    1. User logs in → generate JWT, create session record, return token
    2. Page reload → check database for valid session, restore if found
    3. Token expires → session marked as expired, user redirected to login
    4. Logout → session marked as inactive
    """
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash JWT token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def create_session(
        user: User,
        token: str,
        token_expires_at: datetime,
        client_id: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthSession:
        """
        Create a new server-side session for an authenticated user.
        
        Called after successful login to store the JWT token in database.
        
        Args:
            user: Authenticated user object
            token: JWT token string
            token_expires_at: When the token expires (from JWT)
            client_id: Browser/device identifier (optional)
            user_agent: Browser user-agent string (optional)
        
        Returns:
            AuthSession object with session_id
        """
        db = SessionLocal()
        try:
            session = AuthSession(
                username=user.username,
                token_hash=SessionManager._hash_token(token),
                token_expires_at=token_expires_at,
                client_id=client_id or str(uuid.uuid4()),
                user_agent=user_agent,
                is_active=True,
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session
        finally:
            db.close()
    
    @staticmethod
    def validate_token_in_session(token: str) -> Optional[User]:
        """
        Validate a token by checking:
        1. JWT signature and expiration (JWTManager)
        2. Session exists in database and is valid
        
        Args:
            token: JWT token from client
        
        Returns:
            User object if valid, None otherwise
        """
        # First validate JWT structure and signature
        user = JWTManager.validate_token(token)
        if not user:
            return None
        
        # Then check if session exists in database
        token_hash = SessionManager._hash_token(token)
        db = SessionLocal()
        try:
            session = db.query(AuthSession).filter(
                AuthSession.token_hash == token_hash
            ).first()
            
            if not session:
                return None
            
            # Check if session is still valid
            if not session.is_valid:
                return None
            
            # Update last access time
            session.refresh_access_time()
            db.commit()
            
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_session_by_id(session_id: str) -> Optional[dict]:
        """
        Get session data by session_id.
        Used for security-focused session recovery (not token-based).
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dict with session data if valid, None otherwise
        """
        db = SessionLocal()
        try:
            session = db.query(AuthSession).filter(
                AuthSession.session_id == session_id
            ).first()
            
            if session and session.is_valid and session.is_active:
                session.refresh_access_time()
                db.commit()
                
                return {
                    "session_id": session.session_id,
                    "username": session.username,
                    "is_active": session.is_active,
                    "token_expires_at": session.token_expires_at,
                    "created_at": session.created_at,
                    "client_id": session.client_id,
                }
            
            return None
        finally:
            db.close()
    
    @staticmethod
    def invalidate_session_by_id(session_id: str) -> bool:
        """
        Invalidate a session by session_id (logout).
        Uses session_id instead of token for better security.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was invalidated, False if not found
        """
        db = SessionLocal()
        try:
            session = db.query(AuthSession).filter(
                AuthSession.session_id == session_id
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
                return True
            return False
        finally:
            db.close()
        """
        Retrieve a valid session for a user.
        
        Used during page reload to check if user has a valid session
        without requiring the token to be in memory.
        
        Args:
            username: Username to look up
            client_id: Specific client ID (optional, if None returns any valid session)
        
        Returns:
            Dict with session data if valid session exists, None otherwise
        """
        db = SessionLocal()
        try:
            query = db.query(AuthSession).filter(
                AuthSession.username == username,
                AuthSession.is_active == True,
            )
            
            if client_id:
                query = query.filter(AuthSession.client_id == client_id)
            
            # Get most recent session
            session = query.order_by(AuthSession.last_accessed_at.desc()).first()
            
            if session and session.is_valid:
                session.refresh_access_time()
                db.commit()
                
                # Return dict to avoid detached instance errors
                return {
                    "session_id": session.session_id,
                    "username": session.username,
                    "is_active": session.is_active,
                    "token_expires_at": session.token_expires_at,
                    "created_at": session.created_at,
                    "client_id": session.client_id,
                }
            
            return None
        finally:
            db.close()
    
    @staticmethod
    def invalidate_session(token: str) -> bool:
        """
        Invalidate a session (logout).
        
        Args:
            token: JWT token to invalidate
        
        Returns:
            True if session was invalidated, False if not found
        """
        token_hash = SessionManager._hash_token(token)
        db = SessionLocal()
        try:
            session = db.query(AuthSession).filter(
                AuthSession.token_hash == token_hash
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    @staticmethod
    def invalidate_all_user_sessions(username: str) -> int:
        """
        Invalidate all sessions for a user (e.g., admin force logout).
        
        Args:
            username: Username whose sessions to invalidate
        
        Returns:
            Number of sessions invalidated
        """
        db = SessionLocal()
        try:
            count = db.query(AuthSession).filter(
                AuthSession.username == username
            ).update({"is_active": False})
            db.commit()
            return count
        finally:
            db.close()
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Delete expired sessions from database (maintenance task).
        
        Should be called periodically to clean up old sessions.
        Could be run as a scheduled background job.
        
        Returns:
            Number of sessions deleted
        """
        db = SessionLocal()
        try:
            count = db.query(AuthSession).filter(
                AuthSession.token_expires_at < datetime.utcnow()
            ).delete()
            db.commit()
            return count
        finally:
            db.close()
    
    @staticmethod
    def get_user_active_sessions(username: str) -> list[AuthSession]:
        """
        Get all active sessions for a user.
        
        Useful for:
        - "Where are you logged in?" UI
        - Forcing logout from other devices
        - Security audit
        
        Args:
            username: Username to list sessions for
        
        Returns:
            List of active AuthSession objects
        """
        db = SessionLocal()
        try:
            sessions = db.query(AuthSession).filter(
                AuthSession.username == username,
                AuthSession.is_active == True,
                AuthSession.token_expires_at > datetime.utcnow(),
            ).all()
            return sessions
        finally:
            db.close()
