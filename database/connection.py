"""
Configuración de la base de datos SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment or use default
# For production: set DATABASE_PATH=/var/lib/cognidata/cognidata.db or similar
DATABASE_PATH = os.getenv("DATABASE_PATH", "cognidata.db")

# SQLite URL format: sqlite:///relative/path or sqlite:////absolute/path
if os.path.isabs(DATABASE_PATH):
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
else:
    DATABASE_URL = f"sqlite:///./{ DATABASE_PATH}"

# Ensure database directory exists if using an absolute path
if DATABASE_PATH.startswith("/") and "/" in DATABASE_PATH:
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not create database directory {db_dir}: {e}")
            print(f"Will attempt to create at runtime if needed")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar todas las tablas"""
    from models import patient, test_session, audit_log, user, protocol, session

    Base.metadata.create_all(bind=engine)
    
    # Run migrations
    _migrate_database()


def _migrate_database():
    """Run database migrations"""
    conn = engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        # Add protocol_id column to test_sessions if it doesn't exist
        cursor.execute("PRAGMA table_info(test_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'protocol_id' not in columns:
            cursor.execute("""
                ALTER TABLE test_sessions 
                ADD COLUMN protocol_id TEXT
            """)
            conn.commit()
    finally:
        cursor.close()
        conn.close()
