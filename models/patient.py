"""
Modelo Patient - Paciente anónimo
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base
import uuid


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    age = Column(Integer, nullable=False)
    education_years = Column(Integer, nullable=False)
    laterality = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    encrypted_metadata = Column(String, nullable=True)
    
    sessions = relationship("TestSession", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient {self.id[:8]}... {self.age}años, {self.education_years} años escolaridad>"
