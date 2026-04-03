"""
Protocol Service - Business logic for managing neuropsychological test protocols
"""

from typing import List, Optional
from datetime import datetime
from database.connection import SessionLocal
from models import Protocol, ProtocolTest, PatientProtocol, Patient


class ProtocolService:
    """Service for protocol management operations"""
    
    @staticmethod
    def create_protocol(
        name: str,
        description: str = None,
        category: str = None,
        tests: List[str] = None
    ) -> Protocol:
        """
        Create a new protocol
        
        Args:
            name: Protocol name (must be unique)
            description: Protocol description
            category: Category (e.g., "Rastreio", "Avaliação Completa")
            tests: List of test types to include
        
        Returns:
            Created Protocol object
        """
        db = SessionLocal()
        try:
            protocol = Protocol(
                name=name,
                description=description,
                category=category
            )
            
            if tests:
                for idx, test_type in enumerate(tests, 1):
                    protocol.add_test(test_type, order=idx)
            
            db.add(protocol)
            db.commit()
            db.refresh(protocol)
            return protocol
        finally:
            db.close()
    
    @staticmethod
    def get_protocol(protocol_id: str) -> Optional[Protocol]:
        """Get protocol by ID"""
        db = SessionLocal()
        try:
            return db.query(Protocol).filter(Protocol.id == protocol_id).first()
        finally:
            db.close()
    
    @staticmethod
    def get_protocol_by_name(name: str) -> Optional[Protocol]:
        """Get protocol by name"""
        db = SessionLocal()
        try:
            return db.query(Protocol).filter(Protocol.name == name).first()
        finally:
            db.close()
    
    @staticmethod
    def list_protocols(category: str = None) -> List[Protocol]:
        """
        List all protocols, optionally filtered by category
        
        Args:
            category: Optional category filter
        
        Returns:
            List of Protocol objects
        """
        db = SessionLocal()
        try:
            query = db.query(Protocol)
            if category:
                query = query.filter(Protocol.category == category)
            return query.order_by(Protocol.name).all()
        finally:
            db.close()
    
    @staticmethod
    def list_categories() -> List[str]:
        """Get all unique protocol categories"""
        db = SessionLocal()
        try:
            categories = db.query(Protocol.category).distinct().filter(
                Protocol.category.isnot(None)
            ).all()
            return sorted([c[0] for c in categories])
        finally:
            db.close()
    
    @staticmethod
    def update_protocol(
        protocol_id: str,
        name: str = None,
        description: str = None,
        category: str = None,
        tests: List[str] = None
    ) -> Optional[Protocol]:
        """
        Update an existing protocol
        
        Args:
            protocol_id: Protocol ID
            name: New name (optional)
            description: New description (optional)
            category: New category (optional)
            tests: New list of tests (optional)
        
        Returns:
            Updated Protocol object or None if not found
        """
        db = SessionLocal()
        try:
            protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
            if not protocol:
                return None
            
            if name is not None:
                protocol.name = name
            if description is not None:
                protocol.description = description
            if category is not None:
                protocol.category = category
            
            if tests is not None:
                # Clear existing tests
                protocol.tests.clear()
                # Add new tests
                for idx, test_type in enumerate(tests, 1):
                    protocol.add_test(test_type, order=idx)
            
            protocol.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(protocol)
            return protocol
        finally:
            db.close()
    
    @staticmethod
    def delete_protocol(protocol_id: str) -> bool:
        """
        Delete a protocol
        
        Args:
            protocol_id: Protocol ID
        
        Returns:
            True if deleted, False if not found
        """
        db = SessionLocal()
        try:
            protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
            if not protocol:
                return False
            
            db.delete(protocol)
            db.commit()
            return True
        finally:
            db.close()
    
    @staticmethod
    def assign_protocol_to_patient(
        patient_id: str,
        protocol_id: str,
        assigned_by: str = None,
        notes: str = None
    ) -> Optional[PatientProtocol]:
        """
        Assign a protocol to a patient
        
        Args:
            patient_id: Patient ID
            protocol_id: Protocol ID
            assigned_by: Username who assigned it (optional)
            notes: Additional notes (optional)
        
        Returns:
            Created PatientProtocol object or None if already assigned
        """
        db = SessionLocal()
        try:
            # Check if already assigned
            existing = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id,
                PatientProtocol.protocol_id == protocol_id
            ).first()
            
            if existing:
                return None  # Already assigned
            
            assignment = PatientProtocol(
                patient_id=patient_id,
                protocol_id=protocol_id,
                assigned_by=assigned_by,
                notes=notes
            )
            
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            return assignment
        finally:
            db.close()
    
    @staticmethod
    def unassign_protocol_from_patient(patient_id: str, protocol_id: str) -> bool:
        """
        Remove a protocol assignment from a patient
        
        Args:
            patient_id: Patient ID
            protocol_id: Protocol ID
        
        Returns:
            True if removed, False if not found
        """
        db = SessionLocal()
        try:
            assignment = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id,
                PatientProtocol.protocol_id == protocol_id
            ).first()
            
            if not assignment:
                return False
            
            db.delete(assignment)
            db.commit()
            return True
        finally:
            db.close()
    
    @staticmethod
    def get_patient_protocols(patient_id: str) -> List[PatientProtocol]:
        """
        Get all protocol assignments for a patient
        
        Args:
            patient_id: Patient ID
        
        Returns:
            List of PatientProtocol assignments
        """
        db = SessionLocal()
        try:
            return db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id
            ).all()
        finally:
            db.close()
    
    @staticmethod
    def get_protocol_patients(protocol_id: str) -> List[PatientProtocol]:
        """
        Get all patient assignments for a protocol
        
        Args:
            protocol_id: Protocol ID
        
        Returns:
            List of PatientProtocol assignments
        """
        db = SessionLocal()
        try:
            return db.query(PatientProtocol).filter(
                PatientProtocol.protocol_id == protocol_id
            ).all()
        finally:
            db.close()
    
    @staticmethod
    def update_protocol_status(
        patient_id: str,
        protocol_id: str,
        status: str
    ) -> Optional[PatientProtocol]:
        """
        Update the status of a protocol assignment
        
        Args:
            patient_id: Patient ID
            protocol_id: Protocol ID
            status: New status ('pending', 'in_progress', 'completed')
        
        Returns:
            Updated PatientProtocol or None if not found
        """
        db = SessionLocal()
        try:
            assignment = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id,
                PatientProtocol.protocol_id == protocol_id
            ).first()
            
            if not assignment:
                return None
            
            assignment.status = status
            db.commit()
            db.refresh(assignment)
            return assignment
        finally:
            db.close()
    
    @staticmethod
    def get_available_tests() -> List[str]:
        """
        Get list of all available test types
        
        Returns:
            List of test type strings
        """
        return [
            "TMT-A",
            "TMT-B",
            "TAVEC",
            "Fluidez-FAS",
            "Fluidez-Semántica",
            "Rey-Copia",
            "Rey-Memoria",
            "Torre de Londres",
            "Toulouse-Pieron",
            "DIVA-5",
            "BRIEF-A",
            "WAIS-IV",
            "Dígitos",
            "Test d2-R",
            "FDT",
            "BADS-Zoo",
            "BADS-Llave",
            "FCSRT",
            "Perfil Sensorial"
        ]


# Global instance
protocol_service = ProtocolService()
