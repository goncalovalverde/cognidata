"""
Rate limiting model for brute-force attack prevention
Tracks failed login attempts per IP address
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from database.connection import Base


class RateLimitAttempt(Base):
    """Track failed login attempts per IP address"""
    __tablename__ = "rate_limit_attempts"

    ip_address = Column(String(45), primary_key=True, index=True)
    failed_attempts = Column(Integer, default=0, nullable=False, server_default="0")
    last_attempt_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.failed_attempts = 0
        self.last_attempt_at = datetime.now(timezone.utc)
        self.locked_until = None

    def __repr__(self):
        return f"<RateLimitAttempt(ip={self.ip_address}, attempts={self.failed_attempts})>"

    def is_locked(self):
        """Check if IP is currently locked"""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until

    def lock_for_duration(self, minutes: int = 15):
        """Lock IP for specified duration"""
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    def reset(self):
        """Reset attempt counter"""
        self.failed_attempts = 0
        self.locked_until = None
        self.last_attempt_at = datetime.now(timezone.utc)

    def record_failed_attempt(self, max_attempts: int = 5, lockout_minutes: int = 15):
        """Record a failed attempt and lock if threshold reached"""
        self.failed_attempts += 1
        self.last_attempt_at = datetime.now(timezone.utc)

        if self.failed_attempts >= max_attempts:
            self.lock_for_duration(lockout_minutes)
