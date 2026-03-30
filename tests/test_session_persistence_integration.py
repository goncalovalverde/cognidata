"""
Integration test for session persistence - Demonstrates the real-world scenario
where a user logs in, closes/refreshes browser, and is automatically re-authenticated.

This test simulates the complete lifecycle without mocking Streamlit.
"""

import pytest
from datetime import datetime, timedelta
import time

from database.connection import SessionLocal, Base, engine
from services.session_manager import SessionManager
from utils.jwt_manager import JWTManager
from utils.auth import User


class TestSessionPersistenceIntegration:
    """End-to-end integration tests for session persistence"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_user_login_and_session_recovery(self):
        """
        Integration test: User logs in → session stored → browser reload → 
        user auto-authenticated without showing login form
        """
        # --- PHASE 1: USER LOGS IN ---
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        
        # Backend generates JWT token (24h)
        token = JWTManager.generate_token(user)
        assert token is not None
        
        # Backend creates session record in database
        expires = datetime.utcnow() + timedelta(hours=24)
        session = SessionManager.create_session(user, token, expires)
        assert session is not None
        assert session.username == "clinician"
        assert session.is_active == True
        
        print("✅ Phase 1: User logged in, session created")
        
        # --- PHASE 2: BROWSER RELOADS (OR DIFFERENT REQUEST) ---
        # In real Streamlit, st.session_state is lost here
        # But auth_token might still be in state, or we recover it
        
        # Simulate recovery: We have the token from before
        recovered_user = SessionManager.validate_token_in_session(token)
        assert recovered_user is not None
        assert recovered_user.username == "clinician"
        assert recovered_user.role == "CLINICIAN"
        
        print("✅ Phase 2: Session recovered from database")
        
        # --- PHASE 3: SESSION EXPIRES ---
        # Create an expired session for a different user
        user2 = User(username="viewer", role="VIEWER", full_name="Viewer User")
        expired_token = JWTManager.generate_token(user2)
        expired_time = datetime.utcnow() - timedelta(hours=1)  # Already expired
        SessionManager.create_session(user2, expired_token, expired_time)
        
        # Try to validate expired token
        result = SessionManager.validate_token_in_session(expired_token)
        assert result is None  # Should be None (expired)
        
        print("✅ Phase 3: Expired sessions rejected")
        
        # --- PHASE 4: LOGOUT ---
        SessionManager.invalidate_session(token)
        
        # Try to use invalidated token - should fail
        result = SessionManager.validate_token_in_session(token)
        assert result is None
        
        print("✅ Phase 4: Logout invalidates session")
    
    def test_session_security_token_hash(self):
        """
        Verify that tokens are hashed in database, not stored in plain text.
        
        This test ensures that if database is compromised, attacker can't
        directly reuse tokens stored in DB.
        """
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        token = JWTManager.generate_token(user)
        expires = datetime.utcnow() + timedelta(hours=24)
        
        session = SessionManager.create_session(user, token, expires)
        
        # Token hash should NOT equal the plain token
        import hashlib
        expected_hash = hashlib.sha256(token.encode()).hexdigest()
        
        assert session.token_hash == expected_hash
        assert session.token_hash != token
        
        # Token stored in DB is hashed, not plain
        db = SessionLocal()
        try:
            from models.session import AuthSession
            db_session = db.query(AuthSession).filter_by(
                session_id=session.session_id
            ).first()
            assert db_session.token_hash == expected_hash
            assert db_session.token_hash != token
        finally:
            db.close()
        
        print("✅ Security: Tokens stored as hashes, not plain text")
    
    def test_session_cleanup_maintenance(self):
        """
        Test cleanup of expired sessions (maintenance operation).
        
        Should run periodically to keep database clean.
        """
        user1 = User(username="user1", role="CLINICIAN", full_name="User 1")
        user2 = User(username="user2", role="CLINICIAN", full_name="User 2")
        
        # Create mixed sessions: active and expired
        valid_token = JWTManager.generate_token(user1)
        valid_expires = datetime.utcnow() + timedelta(hours=24)
        SessionManager.create_session(user1, valid_token, valid_expires)
        
        expired_token = JWTManager.generate_token(user2)
        expired_time = datetime.utcnow() - timedelta(hours=1)
        SessionManager.create_session(user2, expired_token, expired_time)
        
        # Verify both exist before cleanup
        db = SessionLocal()
        try:
            from models.session import AuthSession
            count_before = db.query(AuthSession).count()
            assert count_before == 2
        finally:
            db.close()
        
        # Run cleanup
        deleted = SessionManager.cleanup_expired_sessions()
        assert deleted == 1  # Expired session removed
        
        # Verify: only valid session remains
        db = SessionLocal()
        try:
            from models.session import AuthSession
            count_after = db.query(AuthSession).count()
            assert count_after == 1
            remaining = db.query(AuthSession).first()
            assert remaining.username == "user1"
        finally:
            db.close()
        
        print("✅ Maintenance: Cleanup removes expired sessions")
    
    def test_multiple_users_independent_sessions(self):
        """
        Multiple users can be logged in independently.
        User A's logout shouldn't affect User B's session.
        """
        user_a = User(username="clinician_a", role="CLINICIAN", full_name="Dr. A")
        user_b = User(username="clinician_b", role="CLINICIAN", full_name="Dr. B")
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # Both users log in
        token_a = JWTManager.generate_token(user_a)
        session_a = SessionManager.create_session(user_a, token_a, expires)
        
        token_b = JWTManager.generate_token(user_b)
        session_b = SessionManager.create_session(user_b, token_b, expires)
        
        # Both sessions valid
        assert SessionManager.validate_token_in_session(token_a) is not None
        assert SessionManager.validate_token_in_session(token_b) is not None
        
        # User A logs out
        SessionManager.invalidate_session(token_a)
        
        # User A's session gone
        assert SessionManager.validate_token_in_session(token_a) is None
        
        # User B's session still works
        assert SessionManager.validate_token_in_session(token_b) is not None
        
        print("✅ Multi-user: Users independent and isolated")
    
    def test_force_logout_all_devices_same_user(self):
        """
        Admin can force logout a user from all devices.
        """
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create 3 sessions for the same user (different devices)
        token1 = JWTManager.generate_token(user)
        time.sleep(0.05)  # Small delay to differentiate tokens
        
        token2 = JWTManager.generate_token(user)
        time.sleep(0.05)
        
        token3 = JWTManager.generate_token(user)
        
        SessionManager.create_session(user, token1, expires, client_id="device1")
        SessionManager.create_session(user, token2, expires, client_id="device2")
        SessionManager.create_session(user, token3, expires, client_id="device3")
        
        # Verify all are active
        active_before = SessionManager.get_user_active_sessions("clinician")
        assert len(active_before) == 3
        
        # --- ADMIN FORCE LOGOUT ---
        count = SessionManager.invalidate_all_user_sessions("clinician")
        assert count == 3
        
        # No active sessions left
        active_after = SessionManager.get_user_active_sessions("clinician")
        assert len(active_after) == 0
        
        print("✅ Force logout: All devices disconnected")


class TestSessionJWTIntegration:
    """Integration of JWT + Session components"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_jwt_expiration_matches_session_expiration(self):
        """
        Both JWT and session should expire at approximately the same time.
        
        This ensures consistency in token lifecycle management.
        """
        user = User(username="test", role="CLINICIAN", full_name="Test")
        
        # Generate token (creates JWT with exp time)
        token = JWTManager.generate_token(user)
        
        # Decode to get JWT expiration
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        jwt_exp_time = datetime.fromtimestamp(decoded["exp"])
        
        # Create session with matching expiration based on JWT
        # (In production, the session expiration should match JWT exp)
        session = SessionManager.create_session(user, token, jwt_exp_time)
        
        # Times should be very close (within 1 second - rounding difference)
        time_diff = abs((jwt_exp_time - session.token_expires_at).total_seconds())
        assert time_diff < 1  # Almost identical
        
        print("✅ JWT and session expiration times synchronized")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
