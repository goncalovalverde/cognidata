"""
Session Token Storage Manager - Store JWT tokens persistently across page reloads.

ISSUE: streamlit-cookies-manager causes "multiple elements with the same key" error
in Streamlit 1.36+. 

SOLUTION: Use st.session_state + Streamlit's native query parameter storage,
or use browser sessionStorage via JavaScript injection.

For production with strict security requirements, implement server-side sessions.
"""

import streamlit as st
from typing import Optional
import json


class AuthTokenStorage:
    """
    Manages authentication JWT tokens storage using st.session_state.
    
    Note: st.session_state alone does NOT persist across page reloads.
    To achieve persistence, we need to:
    1. Store token in st.session_state (fast, in-memory)
    2. Store in browser via query parameters or localStorage
    3. On page reload, recover from query params
    
    This implementation uses st.session_state as primary storage.
    For true persistence, would need server-side sessions or cookies.
    """
    
    SESSION_STATE_KEY = "auth_token"
    
    @staticmethod
    def save_token(token: str) -> None:
        """
        Save authentication token to session state.
        
        Args:
            token: JWT token string
        """
        # Store in session state (in-memory, fastest)
        st.session_state[AuthTokenStorage.SESSION_STATE_KEY] = token
    
    @staticmethod
    def get_token() -> Optional[str]:
        """
        Retrieve authentication token from session state.
        
        Returns:
            JWT token string if found, None otherwise
        """
        return st.session_state.get(AuthTokenStorage.SESSION_STATE_KEY)
    
    @staticmethod
    def clear_token() -> None:
        """
        Remove authentication token from session state.
        Called on logout.
        """
        if AuthTokenStorage.SESSION_STATE_KEY in st.session_state:
            del st.session_state[AuthTokenStorage.SESSION_STATE_KEY]
    
    @staticmethod
    def token_exists() -> bool:
        """
        Check if authentication token exists in session state.
        
        Returns:
            True if token exists, False otherwise
        """
        return AuthTokenStorage.SESSION_STATE_KEY in st.session_state


class AuthCookieManager:
    """
    Wrapper for backward compatibility.
    Uses st.session_state as underlying storage.
    
    WARNING: This does NOT persist across page reloads!
    To implement true session persistence, use one of:
    1. Server-side sessions (database table)
    2. Browser cookies (requires working cookies-manager library)
    3. URL query parameters (security risk)
    """
    
    @staticmethod
    def set_auth_cookie(token: str, max_age: int = None) -> None:
        """Store JWT token"""
        AuthTokenStorage.save_token(token)
    
    @staticmethod
    def get_auth_cookie() -> Optional[str]:
        """Retrieve JWT token"""
        return AuthTokenStorage.get_token()
    
    @staticmethod
    def clear_auth_cookie() -> None:
        """Remove JWT token"""
        AuthTokenStorage.clear_token()
    
    @staticmethod
    def cookie_exists() -> bool:
        """Check if JWT token exists"""
        return AuthTokenStorage.token_exists()

