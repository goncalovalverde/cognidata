"""
Servicio de auditoría para compliance RGPD
Registra todas las operaciones sobre datos de pacientes
"""

from database.connection import SessionLocal
from models.audit_log import AuditLog
import json
from datetime import datetime
import socket


class AuditService:
    ACTIONS = {
        "PATIENT_CREATE": "patient.create",
        "PATIENT_VIEW": "patient.view",
        "PATIENT_UPDATE": "patient.update",
        "PATIENT_DELETE": "patient.delete",
        "TEST_CREATE": "test.create",
        "TEST_VIEW": "test.view",
        "TEST_DELETE": "test.delete",
        "REPORT_GENERATE": "report.generate",
        "BACKUP_CREATE": "backup.create",
        "DATA_EXPORT": "data.export",
        "LOGIN": "auth.login",
        "LOGOUT": "auth.logout",
    }

    RESOURCE_PATIENT = "patient"
    RESOURCE_TEST_SESSION = "test_session"
    RESOURCE_REPORT = "report"
    RESOURCE_BACKUP = "backup"
    RESOURCE_SYSTEM = "system"

    def __init__(self):
        self._ip_cache = None

    def _get_client_ip(self) -> str:
        if self._ip_cache:
            return self._ip_cache
        try:
            hostname = socket.gethostname()
            self._ip_cache = socket.gethostbyname(hostname)
        except Exception:
            self._ip_cache = "unknown"
        return self._ip_cache

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: dict = None,
        user_identifier: str = None,
    ):
        """
        Registrar un evento de auditoría

        Args:
            action: Tipo de acción (usar ACTIONS constants)
            resource_type: Tipo de recurso (patient, test_session, etc.)
            resource_id: ID del recurso afectado
            details: Diccionario con detalles adicionales
            user_identifier: Identificador del usuario (para futuro auth)
        """
        db = SessionLocal()
        try:
            log_entry = AuditLog(
                timestamp=datetime.utcnow(),
                user_identifier=user_identifier,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id[:12] if resource_id else None,
                details=json.dumps(details, ensure_ascii=False) if details else None,
                ip_address=self._get_client_ip(),
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Audit log error: {e}")
        finally:
            db.close()

    def log_patient_create(self, patient_id: str, patient_data: dict):
        self.log(
            action=self.ACTIONS["PATIENT_CREATE"],
            resource_type=self.RESOURCE_PATIENT,
            resource_id=patient_id,
            details={
                "age": patient_data.get("age"),
                "education_years": patient_data.get("education_years"),
                "laterality": patient_data.get("laterality"),
            },
        )

    def log_patient_view(self, patient_id: str):
        self.log(
            action=self.ACTIONS["PATIENT_VIEW"],
            resource_type=self.RESOURCE_PATIENT,
            resource_id=patient_id,
        )

    def log_patient_delete(self, patient_id: str):
        self.log(
            action=self.ACTIONS["PATIENT_DELETE"],
            resource_type=self.RESOURCE_PATIENT,
            resource_id=patient_id,
        )

    def log_test_create(
        self, session_id: str, patient_id: str, test_type: str, scores: dict
    ):
        self.log(
            action=self.ACTIONS["TEST_CREATE"],
            resource_type=self.RESOURCE_TEST_SESSION,
            resource_id=session_id,
            details={
                "patient_id": patient_id[:12] if patient_id else None,
                "test_type": test_type,
                "puntuacion_escalar": scores.get("puntuacion_escalar")
                if scores
                else None,
                "percentil": scores.get("percentil") if scores else None,
            },
        )

    def log_test_view(self, session_id: str, patient_id: str):
        self.log(
            action=self.ACTIONS["TEST_VIEW"],
            resource_type=self.RESOURCE_TEST_SESSION,
            resource_id=session_id,
            details={"patient_id": patient_id[:12] if patient_id else None},
        )

    def log_report_generate(self, patient_id: str, test_count: int):
        self.log(
            action=self.ACTIONS["REPORT_GENERATE"],
            resource_type=self.RESOURCE_REPORT,
            resource_id=patient_id,
            details={"test_count": test_count},
        )

    def log_backup_create(self, backup_filename: str):
        self.log(
            action=self.ACTIONS["BACKUP_CREATE"],
            resource_type=self.RESOURCE_BACKUP,
            resource_id=backup_filename,
            details={"filename": backup_filename},
        )

    def get_logs(
        self,
        resource_type: str = None,
        resource_id: str = None,
        action: str = None,
        limit: int = 100,
    ):
        """Obtener registros de auditoría con filtros"""
        db = SessionLocal()
        try:
            query = db.query(AuditLog)

            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            if resource_id:
                query = query.filter(AuditLog.resource_id.startswith(resource_id[:12]))
            if action:
                query = query.filter(AuditLog.action == action)

            return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
        finally:
            db.close()

    def get_patient_history(self, patient_id: str, limit: int = 50):
        """Obtener historial completo de auditoria de un paciente"""
        db = SessionLocal()
        try:
            return (
                db.query(AuditLog)
                .filter(
                    (AuditLog.resource_id.startswith(patient_id[:12]))
                    | (AuditLog.details.contains(patient_id[:8]))
                )
                .order_by(AuditLog.timestamp.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()


audit_service = AuditService()
