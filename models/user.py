"""
User model for authentication and role-based access control
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from database.connection import Base
import enum


class UserRole(str, enum.Enum):
    """User roles for role-based access control"""
    ADMIN = "Admin"
    PRACTITIONER = "Practitioner"
    VIEWER = "Viewer"


class User(Base):
    """User account with role-based access control"""
    __tablename__ = "users"

    username = Column(String(50), primary_key=True, unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"

    def get_permissions(self):
        """Get permissions based on role"""
        permissions = {
            UserRole.ADMIN: {
                "view_patients": True,
                "create_patient": True,
                "edit_patient": True,
                "delete_patient": True,
                "enter_tests": True,
                "view_tests": True,
                "delete_tests": True,
                "generate_reports": True,
                "view_dashboard": True,
                "manage_users": True,
                "view_audit_logs": True,
                "create_backups": True,
            },
            UserRole.PRACTITIONER: {
                "view_patients": True,
                "create_patient": True,
                "edit_patient": True,
                "delete_patient": False,
                "enter_tests": True,
                "view_tests": True,
                "delete_tests": False,
                "generate_reports": True,
                "view_dashboard": True,
                "manage_users": False,
                "view_audit_logs": False,
                "create_backups": False,
            },
            UserRole.VIEWER: {
                "view_patients": True,
                "create_patient": False,
                "edit_patient": False,
                "delete_patient": False,
                "enter_tests": False,
                "view_tests": True,
                "delete_tests": False,
                "generate_reports": False,
                "view_dashboard": True,
                "manage_users": False,
                "view_audit_logs": False,
                "create_backups": False,
            },
        }
        return permissions.get(self.role, {})
