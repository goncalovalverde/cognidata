"""
Protocol models for organizing neuropsychological tests
Allows grouping tests into reusable assessment protocols
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base
import uuid
import json


# Association tables for many-to-many relationships
protocol_test_association = Table(
    'protocol_tests',
    Base.metadata,
    Column('protocol_id', String, ForeignKey('protocols.id'), primary_key=True),
    Column('test_type', String, primary_key=True),
    Column('order', Integer, default=1)
)

patient_protocol_association = Table(
    'patient_protocols',
    Base.metadata,
    Column('patient_id', String, ForeignKey('patients.id'), primary_key=True),
    Column('protocol_id', String, ForeignKey('protocols.id'), primary_key=True),
    Column('assigned_date', DateTime, default=datetime.utcnow),
    Column('assigned_by', String),
    Column('status', String, default='pending'),  # pending, in_progress, completed
)


class Protocol(Base):
    """Protocol for grouping related neuropsychological tests"""
    
    __tablename__ = "protocols"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)  # e.g., "Rastreio", "Avaliação Completa"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tests = relationship(
        'ProtocolTest',
        back_populates='protocol',
        cascade='all, delete-orphan',
        lazy='joined'
    )
    patient_assignments = relationship(
        'PatientProtocol',
        back_populates='protocol',
        cascade='all, delete-orphan'
    )
    
    def add_test(self, test_type: str, order: int = None):
        """Add a test to this protocol"""
        if order is None:
            order = len(self.tests) + 1
        
        # Check if test already exists
        existing = [t for t in self.tests if t.test_type == test_type]
        if not existing:
            self.tests.append(ProtocolTest(test_type=test_type, order=order))
    
    def remove_test(self, test_type: str):
        """Remove a test from this protocol"""
        self.tests = [t for t in self.tests if t.test_type != test_type]
    
    def get_tests_ordered(self):
        """Get tests in execution order"""
        return sorted(self.tests, key=lambda t: t.order)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'test_count': len(self.tests),
            'tests': [t.test_type for t in self.get_tests_ordered()],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Protocol {self.name} - {len(self.tests)} tests>"


class ProtocolTest(Base):
    """Junction table linking protocols to tests with order"""
    
    __tablename__ = "protocol_test_mapping"
    
    protocol_id = Column(String, ForeignKey('protocols.id'), primary_key=True)
    test_type = Column(String, primary_key=True)
    order = Column(Integer, default=1)
    
    # Relationships
    protocol = relationship('Protocol', back_populates='tests')
    
    def __repr__(self):
        return f"<ProtocolTest {self.test_type} (order {self.order})>"


class PatientProtocol(Base):
    """Junction table linking patients to assigned protocols"""
    
    __tablename__ = "patient_protocol_assignments"
    
    patient_id = Column(String, ForeignKey('patients.id'), primary_key=True)
    protocol_id = Column(String, ForeignKey('protocols.id'), primary_key=True)
    assigned_date = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(String, nullable=True)  # Username who assigned it
    status = Column(String, default='pending')  # pending, in_progress, completed
    notes = Column(Text, nullable=True)
    
    # Relationships
    patient = relationship('Patient', back_populates='protocol_assignments')
    protocol = relationship('Protocol', back_populates='patient_assignments')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'patient_id': self.patient_id,
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol.name if self.protocol else None,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'assigned_by': self.assigned_by,
            'status': self.status,
            'notes': self.notes,
        }
    
    def __repr__(self):
        return f"<PatientProtocol {self.patient_id} - {self.protocol_id} ({self.status})>"
