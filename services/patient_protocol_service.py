"""
Patient Protocol Service - Manage protocol assignments for patients
"""

from datetime import datetime
from uuid import uuid4
from database.connection import SessionLocal
from models import Patient, Protocol, PatientProtocol


class PatientProtocolService:
    """Service for managing protocol assignments to patients"""

    @staticmethod
    def assign_protocol(patient_id: str, protocol_id: str, assigned_by: str = "system") -> PatientProtocol:
        """
        Assign a protocol to a patient
        
        Args:
            patient_id: Patient UUID
            protocol_id: Protocol UUID
            assigned_by: Username of who assigned the protocol
        
        Returns:
            PatientProtocol: The created assignment
        """
        db = SessionLocal()
        try:
            # Check if assignment already exists
            existing = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id,
                PatientProtocol.protocol_id == protocol_id
            ).first()
            
            if existing:
                return existing
            
            # Create new assignment
            assignment = PatientProtocol(
                patient_id=patient_id,
                protocol_id=protocol_id,
                assigned_date=datetime.now(),
                assigned_by=assigned_by,
                status="pending"
            )
            
            db.add(assignment)
            db.commit()
            return assignment
        finally:
            db.close()

    @staticmethod
    def get_patient_protocols(patient_id: str) -> list:
        """
        Get all protocols assigned to a patient
        
        Args:
            patient_id: Patient UUID
        
        Returns:
            List of PatientProtocol assignments with protocol details
        """
        db = SessionLocal()
        try:
            assignments = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id
            ).all()
            return assignments
        finally:
            db.close()

    @staticmethod
    def update_protocol_status(patient_id: str, protocol_id: str, status: str) -> PatientProtocol:
        """
        Update the status of a protocol assignment
        
        Args:
            patient_id: Patient UUID
            protocol_id: Protocol UUID
            status: New status (pending, in_progress, completed)
        
        Returns:
            PatientProtocol: The updated assignment
        """
        db = SessionLocal()
        try:
            assignment = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id,
                PatientProtocol.protocol_id == protocol_id
            ).first()
            
            if assignment:
                assignment.status = status
                db.commit()
                return assignment
            return None
        finally:
            db.close()

    @staticmethod
    def unassign_protocol(patient_id: str, protocol_id: str) -> bool:
        """
        Remove a protocol assignment from a patient
        
        Args:
            patient_id: Patient UUID
            protocol_id: Protocol UUID
        
        Returns:
            bool: True if successful, False otherwise
        """
        db = SessionLocal()
        try:
            assignment = db.query(PatientProtocol).filter(
                PatientProtocol.patient_id == patient_id,
                PatientProtocol.protocol_id == protocol_id
            ).first()
            
            if assignment:
                db.delete(assignment)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def get_available_protocols(patient_id: str) -> list:
        """
        Get protocols not yet assigned to a patient
        
        Args:
            patient_id: Patient UUID
        
        Returns:
            List of Protocol objects not yet assigned to this patient
        """
        db = SessionLocal()
        try:
            # Get IDs of assigned protocols
            assigned_ids = db.query(PatientProtocol.protocol_id).filter(
                PatientProtocol.patient_id == patient_id
            ).all()
            assigned_ids = [p[0] for p in assigned_ids]
            
            # Get all protocols not in that list
            available = db.query(Protocol).filter(
                ~Protocol.id.in_(assigned_ids)
            ).all()
            
            return available
        finally:
            db.close()

    @staticmethod
    def get_protocol_completion_status(patient_id: str, protocol_id: str) -> dict:
        """
        Get completion status of a protocol for a patient
        
        Args:
            patient_id: Patient UUID
            protocol_id: Protocol UUID
        
        Returns:
            Dict with completion info: {total_tests, completed_tests, percentage, status}
        """
        db = SessionLocal()
        try:
            from models import TestSession, ProtocolTest
            
            # Get protocol
            protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
            if not protocol:
                return None
            
            # Get all tests in protocol
            total_tests = len(protocol.tests)
            if total_tests == 0:
                return {
                    "total_tests": 0,
                    "completed_tests": 0,
                    "percentage": 0,
                    "status": "empty"
                }
            
            # Get completed tests for this patient
            completed = db.query(TestSession).filter(
                TestSession.patient_id == patient_id,
                TestSession.protocol_id == protocol_id
            ).count()
            
            percentage = int((completed / total_tests) * 100) if total_tests > 0 else 0
            
            if completed == 0:
                status = "pending"
            elif completed < total_tests:
                status = "in_progress"
            else:
                status = "completed"
            
            return {
                "total_tests": total_tests,
                "completed_tests": completed,
                "percentage": percentage,
                "status": status
            }
        finally:
            db.close()


# Create a singleton instance
patient_protocol_service = PatientProtocolService()
