"""
Unit tests for session persistence with JWT tokens and cookies.
Tests for JWT Manager, Cookie Manager, and Auth Integration.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt
from uuid import uuid4

from utils.jwt_manager import JWTManager
from utils.auth import User


class TestJWTManager:
    """Tests for JWT token generation and validation"""

    def test_generate_token_creates_valid_jwt(self):
        """Test that generate_token creates a valid JWT"""
        user = User(username="test_user", role="CLINICIAN", full_name="Test Clinician")
        token = JWTManager.generate_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        # Token should have 3 parts separated by dots (header.payload.signature)
        assert len(token.split('.')) == 3

    def test_generate_token_includes_user_data(self):
        """Test that JWT token contains username and role"""
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        token = JWTManager.generate_token(user)
        
        # Decode token without verification to check payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        assert decoded["username"] == "clinician"
        assert decoded["role"] == "CLINICIAN"
        assert decoded["full_name"] == "Dr. Silva"

    def test_generate_token_sets_24h_expiration(self):
        """Test that generated token expires in 24 hours"""
        user = User(username="test", role="VIEWER", full_name="Test User")
        token = JWTManager.generate_token(user)
        
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Check exp is set
        assert "exp" in decoded
        # Check iat is set
        assert "iat" in decoded
        
        # Expiration should be approximately 24 hours from now
        exp_time = datetime.fromtimestamp(decoded["exp"])
        iat_time = datetime.fromtimestamp(decoded["iat"])
        diff = exp_time - iat_time
        
        # Should be close to 24 hours (86400 seconds)
        assert 86300 < diff.total_seconds() < 86500

    def test_validate_token_returns_user_if_valid(self):
        """Test that valid token returns User object"""
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        token = JWTManager.generate_token(user)
        
        validated_user = JWTManager.validate_token(token)
        
        assert validated_user is not None
        assert validated_user.username == "clinician"
        assert validated_user.role == "CLINICIAN"
        assert validated_user.full_name == "Dr. Silva"

    def test_validate_token_returns_none_if_expired(self):
        """Test that expired token returns None"""
        user = User(username="test", role="VIEWER", full_name="Test")
        
        # Create token with very short expiration (past)
        payload = {
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=25),
        }
        expired_token = jwt.encode(payload, JWTManager.SECRET_KEY, algorithm=JWTManager.ALGORITHM)
        
        result = JWTManager.validate_token(expired_token)
        assert result is None

    def test_validate_token_returns_none_if_invalid(self):
        """Test that invalid/malformed token returns None"""
        result = JWTManager.validate_token("invalid.token.here")
        assert result is None

    def test_validate_token_returns_none_if_tampered(self):
        """Test that tampered token is rejected"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        token = JWTManager.generate_token(user)
        
        # Tamper with the token by changing the signature
        parts = token.split('.')
        tampered_token = f"{parts[0]}.{parts[1]}.wrong_signature"
        
        result = JWTManager.validate_token(tampered_token)
        assert result is None

    def test_token_signature_cannot_be_forged(self):
        """Test that token cannot be forged without secret key"""
        user = User(username="admin", role="ADMIN", full_name="Admin User")
        
        # Create payload as if we're an attacker
        payload = {
            "username": "admin",
            "role": "ADMIN",
            "full_name": "Admin User",
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }
        
        # Try to sign with wrong secret
        wrong_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        
        # Should be rejected by JWTManager
        result = JWTManager.validate_token(wrong_token)
        assert result is None


class TestJWTManagerSecurity:
    """Security tests for JWT Manager"""

    def test_secret_key_is_set(self):
        """Test that secret key is configured"""
        assert JWTManager.SECRET_KEY is not None
        assert len(JWTManager.SECRET_KEY) >= 32, "Secret key should be at least 32 bytes"

    def test_algorithm_is_hs256(self):
        """Test that HS256 algorithm is used"""
        assert JWTManager.ALGORITHM == "HS256"

    def test_expiration_hours_is_24(self):
        """Test that expiration is set to 24 hours"""
        assert JWTManager.EXPIRATION_HOURS == 24


@pytest.mark.skipif(True, reason="CookieManager requires Streamlit context - will test in integration")
class TestCookieManager:
    """Tests for cookie storage and retrieval"""

    def test_set_auth_cookie_stores_jwt_token(self):
        """Test that set_auth_cookie stores JWT token"""
        pass

    def test_set_auth_cookie_uses_httponly(self):
        """Test that cookie is HttpOnly"""
        pass

    def test_set_auth_cookie_uses_secure_flag(self):
        """Test that cookie has Secure flag"""
        pass

    def test_set_auth_cookie_uses_samesite_lax(self):
        """Test that cookie has SameSite=Lax"""
        pass

    def test_get_auth_cookie_retrieves_token(self):
        """Test that get_auth_cookie retrieves token"""
        pass

    def test_get_auth_cookie_returns_none_if_missing(self):
        """Test that missing cookie returns None"""
        pass

    def test_clear_auth_cookie_deletes_token(self):
        """Test that clear_auth_cookie removes token"""
        pass


@pytest.mark.skipif(True, reason="Auth integration requires Streamlit context - will test in integration")
class TestAuthSessionRecovery:
    """Tests for session recovery from cookie on page load"""

    def test_recover_session_from_cookie_on_startup(self):
        """Test that session is recovered from valid cookie"""
        pass

    def test_require_auth_skips_login_if_valid_cookie(self):
        """Test that login is skipped with valid cookie"""
        pass

    def test_require_auth_shows_login_if_expired_cookie(self):
        """Test that login shown when cookie is expired"""
        pass

    def test_login_creates_jwt_and_cookie(self):
        """Test that login creates JWT and cookie"""
        pass

    def test_logout_clears_cookie(self):
        """Test that logout clears cookie"""
        pass


class TestJWTManagerIntegration:
    """Integration tests for JWT workflow"""

    def test_generate_and_validate_token_cycle(self):
        """Test complete cycle: generate → validate"""
        user = User(username="clinician", role="CLINICIAN", full_name="Dr. Silva")
        
        # Generate token
        token = JWTManager.generate_token(user)
        assert token is not None
        
        # Validate token
        validated_user = JWTManager.validate_token(token)
        assert validated_user is not None
        assert validated_user.username == user.username
        assert validated_user.role == user.role

    def test_multiple_tokens_are_different(self):
        """Test that tokens generated at significantly different times are different"""
        user = User(username="test", role="CLINICIAN", full_name="Test")
        
        token1 = JWTManager.generate_token(user)
        
        # Sleep longer to ensure different iat
        import time
        time.sleep(1.1)  # Sleep 1+ second to ensure different timestamp
        token2 = JWTManager.generate_token(user)
        
        # Tokens should be different (due to different iat)
        assert token1 != token2, "Tokens generated at different times should be different"

    def test_token_with_admin_role(self):
        """Test token creation and validation for ADMIN role"""
        admin = User(username="admin", role="ADMIN", full_name="Admin User")
        token = JWTManager.generate_token(admin)
        
        validated = JWTManager.validate_token(token)
        assert validated.role == "ADMIN"

    def test_token_with_viewer_role(self):
        """Test token creation and validation for VIEWER role"""
        viewer = User(username="viewer", role="VIEWER", full_name="Viewer User")
        token = JWTManager.generate_token(viewer)
        
        validated = JWTManager.validate_token(token)
        assert validated.role == "VIEWER"
