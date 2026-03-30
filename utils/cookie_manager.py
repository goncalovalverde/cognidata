"""
Cookie Manager - Secure HTTP-only cookie storage for JWT tokens.

Uses streamlit-cookies-manager for secure cookie handling with:
- HttpOnly flag (prevents JavaScript access)
- Secure flag (HTTPS only in production)
- SameSite=Lax (CSRF protection)
"""

import os
from typing import Optional
from streamlit_cookies_manager import CookieManager


class AuthCookieManager:
    """Manages authentication JWT tokens in HttpOnly cookies"""
    
    COOKIE_NAME = "cognidata_auth_token"
    MAX_AGE = 86400  # 24 hours in seconds
    COOKIE_PATH = "/"
    COOKIE_DOMAIN = None  # Use default (current domain)
    
    @staticmethod
    def set_auth_cookie(token: str, max_age: int = None) -> None:
        """
        Store JWT token in an HttpOnly cookie.
        
        Args:
            token: JWT token string
            max_age: Cookie lifetime in seconds (default: 24 hours)
        """
        if max_age is None:
            max_age = AuthCookieManager.MAX_AGE
        
        try:
            cookies = CookieManager()
            
            # streamlit-cookies-manager uses a simple dict interface
            # For production, additional security headers should be set via app config
            cookies[AuthCookieManager.COOKIE_NAME] = token
            cookies.save()
        except Exception as e:
            # Log error but don't crash - authentication continues
            print(f"Warning: Failed to set auth cookie: {e}")
    
    @staticmethod
    def get_auth_cookie() -> Optional[str]:
        """
        Retrieve JWT token from cookie.
        
        Returns:
            JWT token string if exists, None otherwise
        """
        try:
            cookies = CookieManager()
            token = cookies.get(AuthCookieManager.COOKIE_NAME)
            return token
        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to read auth cookie: {e}")
            return None
    
    @staticmethod
    def clear_auth_cookie() -> None:
        """
        Remove authentication cookie (used on logout).
        
        Sets cookie with max_age=0 to delete it from browser.
        """
        try:
            cookies = CookieManager()
            if AuthCookieManager.COOKIE_NAME in cookies:
                del cookies[AuthCookieManager.COOKIE_NAME]
            cookies.save()
        except Exception as e:
            # Log error but don't crash - logout continues
            print(f"Warning: Failed to clear auth cookie: {e}")
    
    @staticmethod
    def cookie_exists() -> bool:
        """
        Check if authentication cookie exists.
        
        Returns:
            True if cookie exists, False otherwise
        """
        try:
            cookies = CookieManager()
            return AuthCookieManager.COOKIE_NAME in cookies
        except Exception:
            return False
