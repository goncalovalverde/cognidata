"""
JWT Token Manager - Generate and validate JWT tokens for session persistence.

Uses PyJWT library with HS256 algorithm for secure token signing and validation.
"""

import jwt
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User data structure for authentication"""
    username: str
    role: str  # ADMIN, CLINICIAN, VIEWER
    full_name: str = ""


class JWTManager:
    """Manages JWT token generation and validation for session persistence"""
    
    # Configuration - CRITICAL: SECRET_KEY MUST be set via environment variable
    SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
    ALGORITHM = "HS256"
    EXPIRATION_HOURS = 24
    
    @classmethod
    def _validate_secret_key(cls) -> str:
        """
        Validate that SECRET_KEY is properly configured.
        GDPR Article 32: Ensure cryptographic keys are securely managed.
        DevSecOps: Secret Management, Defense in Depth.
        
        Returns:
            str: The validated SECRET_KEY
            
        Raises:
            SystemExit: If SECRET_KEY is not set or too short
        """
        if not cls.SECRET_KEY:
            print(
                "FATAL: AUTH_SECRET_KEY environment variable is not set\n"
                "CogniData requires a secure JWT secret key for authentication.\n\n"
                "To generate a secure key, run:\n"
                "  python -c 'import secrets; print(secrets.token_urlsafe(32))'\n\n"
                "Then set the environment variable:\n"
                "  export AUTH_SECRET_KEY='<generated_key>'\n\n"
                "For production, store this in a secure vault (AWS Secrets Manager, Azure Key Vault, etc.)",
                file=sys.stderr
            )
            sys.exit(1)
        
        if len(cls.SECRET_KEY) < 32:
            print(
                f"FATAL: AUTH_SECRET_KEY must be at least 32 characters (got {len(cls.SECRET_KEY)})\n"
                "Generate a longer key with:\n"
                "  python -c 'import secrets; print(secrets.token_urlsafe(32))'",
                file=sys.stderr
            )
            sys.exit(1)
        
        return cls.SECRET_KEY
    
    @staticmethod
    def generate_token(user: User) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user: User object with username, role, full_name
            
        Returns:
            str: Encoded JWT token (valid for 24 hours)
        """
        # Validate secret key is properly configured
        secret_key = JWTManager._validate_secret_key()
        
        # Create payload with user data
        now = datetime.utcnow()
        payload = {
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "iat": now,  # Issued at
            "exp": now + timedelta(hours=JWTManager.EXPIRATION_HOURS),  # Expiration
        }
        
        # Encode and sign token
        token = jwt.encode(payload, secret_key, algorithm=JWTManager.ALGORITHM)
        return token
    
    @staticmethod
    def validate_token(token: str) -> Optional[User]:
        """
        Validate a JWT token and extract user data.
        
        Args:
            token: JWT token string
            
        Returns:
            User object if token is valid and not expired, None otherwise
        """
        try:
            # Validate secret key is properly configured
            secret_key = JWTManager._validate_secret_key()
            
            # Decode and verify token signature and expiration
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[JWTManager.ALGORITHM]
            )
            
            # Extract user data from payload
            user = User(
                username=payload.get("username"),
                role=payload.get("role"),
                full_name=payload.get("full_name", "")
            )
            
            return user
            
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidSignatureError:
            # Token signature is invalid (tampered)
            return None
        except (jwt.DecodeError, KeyError, ValueError):
            # Token is malformed or missing required fields
            return None
        except Exception:
            # Catch any other exceptions
            return None
