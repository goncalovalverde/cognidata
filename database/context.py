"""
Database context managers for safe session handling
Ensures proper commit/rollback and resource cleanup
"""

from contextlib import contextmanager
from typing import Generator

from database.connection import SessionLocal


@contextmanager
def get_db_session() -> Generator:
    """
    Context manager for database sessions with automatic commit/rollback.

    Usage:
        with get_db_session() as db:
            db.add(patient)
            db.commit()  # Optional - auto-commits on success

    Or simply:
        with get_db_session() as db:
            db.add(patient)
            # Auto-commits and closes on exit

    Raises:
        Exception: Re-raises any exception after rollback
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    """
    Generator-style dependency for FastAPI compatibility.
    Can be used with FastAPI's Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
