"""
Modelo AuditLog - Registro de auditoría para RGPD compliance
"""

from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from database.connection import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_identifier = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type} at {self.timestamp}>"
