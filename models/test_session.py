"""
Modelo TestSession - Sesión de test neuropsicológico
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base
import uuid
import json


class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    test_type = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(Text)
    calculated_scores = Column(Text, nullable=True)
    qualitative_data = Column(Text, nullable=True)
    
    patient = relationship("Patient", back_populates="sessions")
    
    def set_raw_data(self, data: dict):
        self.raw_data = json.dumps(data, ensure_ascii=False)
    
    def get_raw_data(self) -> dict:
        return json.loads(self.raw_data) if self.raw_data else {}
    
    def set_calculated_scores(self, scores: dict):
        self.calculated_scores = json.dumps(scores, ensure_ascii=False)
    
    def get_calculated_scores(self) -> dict:
        return json.loads(self.calculated_scores) if self.calculated_scores else {}
    
    def set_qualitative_data(self, data: dict):
        self.qualitative_data = json.dumps(data, ensure_ascii=False)
    
    def get_qualitative_data(self) -> dict:
        return json.loads(self.qualitative_data) if self.qualitative_data else {}
    
    def __repr__(self):
        return f"<TestSession {self.test_type} - {self.date.strftime('%Y-%m-%d')}>"
