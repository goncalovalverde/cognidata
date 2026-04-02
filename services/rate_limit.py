"""
Rate limiting service for authentication brute-force protection
Implements IP-based rate limiting with exponential lockout
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.rate_limit import RateLimitAttempt
import streamlit as st


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


class RateLimitService:
    """
    Rate limiting service for authentication.
    - Max 5 failed attempts per IP
    - Lockout for 15 minutes after threshold
    - Automatic reset after 24 hours of no attempts
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    RESET_HOURS = 24

    @staticmethod
    def get_client_ip():
        """Extract client IP from Streamlit headers"""
        try:
            # Streamlit forwards X-Forwarded-For header from reverse proxy
            forwarded = st.request.headers.get("X-Forwarded-For", "")
            if forwarded:
                return forwarded.split(",")[0].strip()
            # Fallback to direct connection IP
            return st.request.remote_addr or "127.0.0.1"
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def check_rate_limit(db: Session, ip_address: str) -> bool:
        """
        Check if IP is rate-limited.
        Returns True if allowed, False if locked out.
        Raises RateLimitExceeded if locked.
        """
        attempt = db.query(RateLimitAttempt).filter_by(ip_address=ip_address).first()

        if attempt is None:
            return True  # First attempt, always allowed

        # Check if locked
        if attempt.is_locked():
            remaining_minutes = (
                (attempt.locked_until - datetime.now(timezone.utc)).total_seconds() / 60
            )
            raise RateLimitExceeded(
                f"Too many failed login attempts. Please try again in {int(remaining_minutes)} minutes."
            )

        # Auto-reset if 24 hours since last attempt
        hours_since_last = (
            (datetime.now(timezone.utc) - attempt.last_attempt_at).total_seconds() / 3600
        )
        if hours_since_last > RateLimitService.RESET_HOURS:
            attempt.reset()
            db.commit()
            return True

        return True  # Not locked, allow attempt

    @staticmethod
    def record_failed_attempt(db: Session, ip_address: str) -> None:
        """Record a failed login attempt for an IP"""
        attempt = db.query(RateLimitAttempt).filter_by(ip_address=ip_address).first()

        if attempt is None:
            attempt = RateLimitAttempt(ip_address=ip_address)
            db.add(attempt)

        attempt.record_failed_attempt(
            max_attempts=RateLimitService.MAX_ATTEMPTS,
            lockout_minutes=RateLimitService.LOCKOUT_MINUTES,
        )
        db.commit()

    @staticmethod
    def record_successful_attempt(db: Session, ip_address: str) -> None:
        """Reset rate limit counter on successful login"""
        attempt = db.query(RateLimitAttempt).filter_by(ip_address=ip_address).first()

        if attempt is not None:
            attempt.reset()
            db.commit()

    @staticmethod
    def clear_ip_lock(db: Session, ip_address: str) -> None:
        """Admin function to unlock an IP address"""
        attempt = db.query(RateLimitAttempt).filter_by(ip_address=ip_address).first()

        if attempt is not None:
            attempt.reset()
            db.commit()

    @staticmethod
    def get_lock_status(db: Session, ip_address: str) -> dict:
        """Get current lock status for an IP"""
        attempt = db.query(RateLimitAttempt).filter_by(ip_address=ip_address).first()

        if attempt is None:
            return {
                "ip_address": ip_address,
                "is_locked": False,
                "failed_attempts": 0,
                "locked_until": None,
            }

        return {
            "ip_address": ip_address,
            "is_locked": attempt.is_locked(),
            "failed_attempts": attempt.failed_attempts,
            "locked_until": attempt.locked_until,
            "time_remaining_minutes": (
                ((attempt.locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
                if attempt.is_locked()
                else 0
            ),
        }
