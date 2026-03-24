"""
Base service class with safe database session management
"""

from database.connection import SessionLocal


class BaseService:
    """
    Base class for all services providing safe database access.

    Usage:
        class PatientService(BaseService):
            def get_patients(self):
                with self.get_session() as db:
                    return db.query(Patient).all()

    All database operations are wrapped with automatic commit/rollback.
    """

    def get_session(self):
        """
        Context manager for database sessions.

        Yields:
            Session: SQLAlchemy session with auto-commit on success
                    and auto-rollback on exception.

        Example:
            with self.get_session() as db:
                db.add(patient)
                db.commit()  # Optional
        """
        from database.context import get_db_session

        return get_db_session()

    def execute_in_session(self, func):
        """
        Execute a function within a database session.

        Args:
            func: Function that takes db session as argument

        Returns:
            Result of the function

        Example:
            result = self.execute_in_session(
                lambda db: db.query(Patient).all()
            )
        """
        with self.get_session() as db:
            return func(db)
