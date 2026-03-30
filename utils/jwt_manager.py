"""
JWT Token Manager - Generate and validate JWT tokens for session persistence.

Uses PyJWT library with HS256 algorithm for secure token signing and validation.
"""

import jwt
import os
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
    
    # Configuration
    SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "cognidata-default-insecure-key-change-in-production-min-32-chars")
    ALGORITHM = "HS256"
    EXPIRATION_HOURS = 24
    
    @staticmethod
    def generate_token(user: User) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user: User object with username, role, full_name
            
        Returns:
            str: Encoded JWT token (valid for 24 hours)
        """
        # Ensure secret key is at least 32 bytes (for security)
        if len(JWTManager.SECRET_KEY) < 32:
            # Use a longer default if env var is not set
            secret_key = "cognidata-secure-default-key-for-jwt-signing-at-least-32-bytes-long"
        else:
            secret_key = JWTManager.SECRET_KEY
        
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
            # Ensure secret key is at least 32 bytes
            if len(JWTManager.SECRET_KEY) < 32:
                secret_key = "cognidata-secure-default-key-for-jwt-signing-at-least-32-bytes-long"
            else:
                secret_key = JWTManager.SECRET_KEY
            
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
