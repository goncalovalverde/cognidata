"""
Unit tests for SessionManager - Server-side session storage.

Tests for creating, validating, and managing authentication sessions
stored in the database.

TDD Approach: Write tests first, then implement to make them pass.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from services.session_manager import SessionManager
from models.session import AuthSession
from utils.auth import User
from database.connection import SessionLocal, Base, engine


class TestSessionManagerCreation:
    """Tests for creating server-side sessions"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and drop test database"""
        Base.metadata.create_all(bind=engine)
        yield
        # Cleanup
        Base.metadata.drop_all(bind=engine)
    
    def test_create_session_stores_user_session(self):
        """Test that create_session creates a session record"""
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        token = "test_jwt_token_123"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        session = SessionManager.create_session(
            user=user,
            token=token,
            token_expires_at=expires,
        )
        
        assert session is not None
        assert session.username == "clinician"
        assert session.is_active == True
        assert session.token_expires_at == expires
    
    def test_create_session_hashes_token(self):
        """Test that token is hashed, not stored in plain"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "secret_token_xyz"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        session = SessionManager.create_session(user, token, expires)
        
        # Token should be hashed
        import hashlib
        expected_hash = hashlib.sha256(token.encode()).hexdigest()
        assert session.token_hash == expected_hash
        # Hash should not equal plain token
        assert session.token_hash != token
    
    def test_create_session_generates_session_id(self):
        """Test that session gets a unique UUID"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "token_1"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        session1 = SessionManager.create_session(user, token, expires)
        
        user2 = User(username="test2", role="VIEWER", full_name="Test 2")
        token2 = "token_2"
        session2 = SessionManager.create_session(user2, token2, expires)
        
        # Session IDs should be different
        assert session1.session_id != session2.session_id
    
    def test_create_session_with_client_id(self):
        """Test that create_session can store client ID (browser identifier)"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "token"
        expires = datetime.utcnow() + timedelta(hours=24)
        client_id = "browser_fingerprint_123"
        
        session = SessionManager.create_session(
            user=user,
            token=token,
            token_expires_at=expires,
            client_id=client_id,
        )
        
        assert session.client_id == client_id


class TestSessionManagerValidation:
    """Tests for validating sessions"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and drop test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_validate_token_in_session_accepts_valid_token(self):
        """Test that valid token returns User"""
        # Create session with valid token
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        token = "valid_token_to_store"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # First create a session (which stores the token hash)
        SessionManager.create_session(user, token, expires)
        
        # Now validate - but we can't actually use real JWT without mocking JWTManager
        # So we'll mock JWTManager.validate_token to return our user
        with patch('services.session_manager.JWTManager.validate_token') as mock_validate:
            mock_validate.return_value = user
            
            result = SessionManager.validate_token_in_session(token)
            
            assert result is not None
            assert result.username == "clinician"
    
    def test_validate_token_in_session_rejects_invalid_token(self):
        """Test that invalid JWT returns None"""
        with patch('services.session_manager.JWTManager.validate_token') as mock_validate:
            mock_validate.return_value = None
            
            result = SessionManager.validate_token_in_session("invalid_token")
            
            assert result is None
    
    def test_validate_token_in_session_rejects_expired_session(self):
        """Test that expired session token returns None"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "expired_token"
        
        # Create session with expired time
        expires = datetime.utcnow() - timedelta(hours=1)  # Already expired
        SessionManager.create_session(user, token, expires)
        
        with patch('services.session_manager.JWTManager.validate_token') as mock_validate:
            mock_validate.return_value = user
            
            result = SessionManager.validate_token_in_session(token)
            
            # Should return None because session is expired
            assert result is None
    
    def test_validate_token_updates_last_accessed_at(self):
        """Test that validation updates last access time"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "token"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        session = SessionManager.create_session(user, token, expires)
        original_access = session.last_accessed_at
        
        # Sleep a tiny bit to ensure time passes
        import time
        time.sleep(0.1)
        
        with patch('services.session_manager.JWTManager.validate_token') as mock_validate:
            mock_validate.return_value = user
            
            SessionManager.validate_token_in_session(token)
        
        # Check that last_accessed_at was updated
        db = SessionLocal()
        try:
            updated_session = db.query(AuthSession).filter(
                AuthSession.session_id == session.session_id
            ).first()
            assert updated_session.last_accessed_at > original_access
        finally:
            db.close()


class TestSessionManagerRetrieval:
    """Tests for retrieving sessions"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and drop test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_get_valid_session_finds_active_session(self):
        """Test that get_valid_session returns active session"""
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        token = "token"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        SessionManager.create_session(user, token, expires)
        
        session = SessionManager.get_valid_session("clinician")
        
        assert session is not None
        assert session["username"] == "clinician"
    
    def test_get_valid_session_returns_none_if_expired(self):
        """Test that expired sessions are not returned"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "token"
        
        # Create with expired time
        expires = datetime.utcnow() - timedelta(hours=1)
        SessionManager.create_session(user, token, expires)
        
        session = SessionManager.get_valid_session("test")
        
        assert session is None
    
    def test_get_valid_session_returns_none_if_inactive(self):
        """Test that inactive sessions are not returned"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "token"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        session = SessionManager.create_session(user, token, expires)
        
        # Mark as inactive
        db = SessionLocal()
        try:
            s = db.query(AuthSession).filter(
                AuthSession.session_id == session.session_id
            ).first()
            s.is_active = False
            db.commit()
        finally:
            db.close()
        
        result = SessionManager.get_valid_session("test")
        assert result is None
    
    def test_get_valid_session_with_client_id(self):
        """Test that get_valid_session can filter by client ID"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token1 = "token1"
        token2 = "token2"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create two sessions with different client IDs
        session1 = SessionManager.create_session(
            user, token1, expires, client_id="browser1"
        )
        session2 = SessionManager.create_session(
            user, token2, expires, client_id="browser2"
        )
        
        # Get session for specific client
        result = SessionManager.get_valid_session("test", client_id="browser1")
        
        assert result is not None
        assert result["client_id"] == "browser1"


class TestSessionManagerInvalidation:
    """Tests for invalidating sessions"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and drop test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_invalidate_session_marks_inactive(self):
        """Test that invalidate_session marks session as inactive"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = "token_to_invalidate"
        expires = datetime.utcnow() + timedelta(hours=24)
        
        SessionManager.create_session(user, token, expires)
        
        # Invalidate
        result = SessionManager.invalidate_session(token)
        
        assert result == True
        
        # Check that session is inactive
        db = SessionLocal()
        try:
            session = db.query(AuthSession).filter(
                AuthSession.username == "test"
            ).first()
            assert session.is_active == False
        finally:
            db.close()
    
    def test_invalidate_session_returns_false_if_token_not_found(self):
        """Test that invalidate returns False if token doesn't exist"""
        result = SessionManager.invalidate_session("nonexistent_token")
        assert result == False
    
    def test_invalidate_all_user_sessions(self):
        """Test that invalidate_all_user_sessions invalidates all user's sessions"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create multiple sessions
        SessionManager.create_session(user, "token1", expires)
        SessionManager.create_session(user, "token2", expires)
        SessionManager.create_session(user, "token3", expires)
        
        # Invalidate all
        count = SessionManager.invalidate_all_user_sessions("test")
        
        assert count == 3
        
        # Verify all are inactive
        db = SessionLocal()
        try:
            active_sessions = db.query(AuthSession).filter(
                AuthSession.username == "test",
                AuthSession.is_active == True
            ).count()
            assert active_sessions == 0
        finally:
            db.close()


class TestSessionManagerCleanup:
    """Tests for session cleanup and maintenance"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and drop test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_cleanup_expired_sessions(self):
        """Test that cleanup removes expired sessions"""
        user1 = User(username="user1", role="CLINICIAN", full_name="User 1")
        user2 = User(username="user2", role="CLINICIAN", full_name="User 2")
        
        # Create one expired, one valid
        expired_time = datetime.utcnow() - timedelta(hours=1)
        valid_time = datetime.utcnow() + timedelta(hours=24)
        
        SessionManager.create_session(user1, "old_token", expired_time)
        SessionManager.create_session(user2, "new_token", valid_time)
        
        # Cleanup
        deleted_count = SessionManager.cleanup_expired_sessions()
        
        assert deleted_count == 1
        
        # Verify expired session is gone
        db = SessionLocal()
        try:
            sessions = db.query(AuthSession).all()
            assert len(sessions) == 1
            assert sessions[0].username == "user2"
        finally:
            db.close()
    
    def test_get_user_active_sessions(self):
        """Test that get_user_active_sessions lists all active sessions"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create active sessions
        SessionManager.create_session(user, "token1", expires)
        SessionManager.create_session(user, "token2", expires)
        
        # Create expired session
        expired = datetime.utcnow() - timedelta(hours=1)
        SessionManager.create_session(user, "token3", expired)
        
        # Get active sessions
        sessions = SessionManager.get_user_active_sessions("test")
        
        # Should only return active, non-expired sessions
        assert len(sessions) == 2
