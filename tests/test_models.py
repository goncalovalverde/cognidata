"""
Unit tests for database models
"""

import pytest
import json
from datetime import datetime
from models.patient import Patient
from models.test_session import TestSession
from models.audit_log import AuditLog


class TestPatientModel:
    """Tests for Patient model"""

    def test_patient_creation(self):
        """Test creating a patient instance"""
        patient = Patient(age=65, education_years=12, laterality="diestro")

        assert patient.age == 65
        assert patient.education_years == 12
        assert patient.laterality == "diestro"

    def test_patient_with_id(self):
        """Test creating a patient with explicit ID"""
        import uuid

        patient = Patient(
            id=str(uuid.uuid4()), age=65, education_years=12, laterality="diestro"
        )

        assert patient.id is not None
        assert len(patient.id) == 36  # UUID format

    def test_patient_repr(self, sample_patient_data):
        """Test patient string representation"""
        import uuid

        patient = Patient(
            id=str(uuid.uuid4()), age=65, education_years=12, laterality="diestro"
        )
        repr_str = repr(patient)

        assert "Patient" in repr_str
        assert "65años" in repr_str


class TestTestSessionModel:
    """Tests for TestSession model"""

    def test_set_raw_data(self):
        """Test setting raw data as JSON"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        raw_data = {"tiempo_segundos": 45, "errores": 0}
        session.set_raw_data(raw_data)

        assert session.raw_data == json.dumps(raw_data, ensure_ascii=False)

    def test_get_raw_data(self):
        """Test getting raw data as dictionary"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        raw_data = {"tiempo_segundos": 45, "errores": 0}
        session.set_raw_data(raw_data)

        retrieved = session.get_raw_data()
        assert retrieved == raw_data
        assert retrieved["tiempo_segundos"] == 45

    def test_get_raw_data_empty(self):
        """Test getting raw data when none set"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        retrieved = session.get_raw_data()
        assert retrieved == {}

    def test_set_calculated_scores(self):
        """Test setting calculated scores as JSON"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        scores = {
            "puntuacion_escalar": 12,
            "percentil": 75,
            "clasificacion": "Superior",
        }
        session.set_calculated_scores(scores)

        assert session.calculated_scores == json.dumps(scores, ensure_ascii=False)

    def test_get_calculated_scores(self):
        """Test getting calculated scores as dictionary"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        scores = {
            "puntuacion_escalar": 12,
            "percentil": 75,
            "clasificacion": "Superior",
        }
        session.set_calculated_scores(scores)

        retrieved = session.get_calculated_scores()
        assert retrieved == scores
        assert retrieved["puntuacion_escalar"] == 12

    def test_get_calculated_scores_empty(self):
        """Test getting calculated scores when none set"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        retrieved = session.get_calculated_scores()
        assert retrieved == {}

    def test_set_qualitative_data(self):
        """Test setting qualitative data as JSON"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        qualitative = {
            "observaciones_proceso": "Buen rapport",
            "checklist": {"atencion": True, "memoria": False},
        }
        session.set_qualitative_data(qualitative)

        assert session.qualitative_data == json.dumps(qualitative, ensure_ascii=False)

    def test_get_qualitative_data(self):
        """Test getting qualitative data as dictionary"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        qualitative = {
            "observaciones_proceso": "Buen rapport",
            "checklist": {"atencion": True},
        }
        session.set_qualitative_data(qualitative)

        retrieved = session.get_qualitative_data()
        assert retrieved == qualitative

    def test_get_qualitative_data_empty(self):
        """Test getting qualitative data when none set"""
        session = TestSession(patient_id="test-patient-id", test_type="TMT-A")

        retrieved = session.get_qualitative_data()
        assert retrieved == {}

    def test_test_session_repr(self):
        """Test test session string representation"""
        session = TestSession(patient_id="test-patient-id", test_type="TAVEC")
        session.date = datetime(2026, 3, 23)

        repr_str = repr(session)
        assert "TAVEC" in repr_str
        assert "2026-03-23" in repr_str

    def test_full_tavec_workflow(self):
        """Test complete TAVEC data workflow"""
        session = TestSession(patient_id="test-patient-id", test_type="TAVEC")

        raw_data = {
            "ensayos": [8, 10, 12, 13, 14],
            "total_lista_a": 57,
            "lista_b": 6,
            "recuerdo_inmediato": 12,
            "recuerdo_diferido": 11,
            "reconocimiento": 15,
        }

        scores = {
            "puntuacion_escalar": 11,
            "percentil": 63,
            "z_score": 0.33,
            "clasificacion": "Normal",
        }

        session.set_raw_data(raw_data)
        session.set_calculated_scores(scores)

        assert session.get_raw_data()["total_lista_a"] == 57
        assert session.get_calculated_scores()["clasificacion"] == "Normal"


class TestAuditLogModel:
    """Tests for AuditLog model"""

    def test_audit_log_creation(self):
        """Test creating an audit log entry"""
        log = AuditLog(
            action="patient.create",
            resource_type="patient",
            resource_id="test-123",
            details='{"age": 65}',
        )

        assert log.action == "patient.create"
        assert log.resource_type == "patient"
        assert log.resource_id == "test-123"

    def test_audit_log_repr(self):
        """Test audit log string representation"""
        log = AuditLog(
            action="test.create",
            resource_type="test_session",
            resource_id="session-456",
        )
        log.timestamp = datetime(2026, 3, 23, 10, 30)

        repr_str = repr(log)
        assert "test.create" in repr_str
        assert "test_session" in repr_str

    def test_audit_log_without_resource_id(self):
        """Test audit log without resource ID"""
        log = AuditLog(action="auth.login", resource_type="system")

        assert log.resource_id is None
