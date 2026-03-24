# [Critical] Database Session Management - Resource Leak Risk

## Context
The application has inconsistent database session management:

1. **Unused FastAPI-style dependency** exists but is never used:
   ```python
   # database/connection.py - NEVER CALLED
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

2. **Manual session handling everywhere** with no transaction safety:
   ```python
   # app.py - Repeated pattern, no rollback on exception
   db = SessionLocal()
   # ... operations ...
   db.commit()
   db.close()  # If exception happens before, session leaks!
   ```

3. **No context manager usage** for database operations

## Impact
- **Resource leaks** when exceptions occur mid-transaction
- **No automatic rollback** on errors
- **Inconsistent behavior** - some paths close, some don't
- **Hard to test** due to direct instantiation
- **Potential data corruption** if commits fail silently

## Current Problem Pattern
```python
# app.py line 113-120 - BUG: Typo in variable name!
if st.button(f"🗑️ Eliminar", key=f"del_{patient.id}"):
    audit_service.log_patient_delete(patient.id)
    db = db_session = SessionLocal()  # Typo! Two variables assigned
    db.delete(patient)
    db.commit()
    db.close()
    st.success("Paciente eliminado")
    st.rerun()  # This function doesn't exist in Streamlit
```

## Proposed Remediation

### Option 1: Context Managers (Recommended)
```python
# database/context.py
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Usage:
with get_db_session() as db:
    db.add(patient)
    db.commit()
    # Automatic rollback if exception, automatic close
```

### Option 2: Session Factory with Cleanup
```python
# services/base_service.py
class BaseService:
    def __init__(self):
        self._session = None
    
    def _with_session(self, func):
        self._session = SessionLocal()
        try:
            result = func(self._session)
            self._session.commit()
            return result
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()
```

### Fix the Bug in app.py
```python
# Before (buggy):
db = db_session = SessionLocal()

# After (fixed):
db = SessionLocal()
```

## Labels
`bug`, `database`, `high-priority`, `refactoring`

## Effort Estimate
4-6 hours
