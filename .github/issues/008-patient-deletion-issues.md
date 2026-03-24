# Patient Deletion Issues - No Confirmation, No Soft Delete

## Context
Patient deletion has multiple issues in `app.py`:

### Issue 1: No Confirmation Dialog
```python
# app.py lines 113-120
if st.button(f"🗑️ Eliminar", key=f"del_{patient.id}"):
    # Immediately deletes - no confirmation!
    audit_service.log_patient_delete(patient.id)
    db.delete(patient)
```

### Issue 2: No Soft Delete
For medical/health data, permanent deletion may violate:
- Data retention regulations
- Audit trail completeness
- Patient right to access (Article 15 GDPR - need to retain data to show)

### Issue 3: Variable Name Typo
```python
# BUG: Typo creates two variables
db = db_session = SessionLocal()
```

### Issue 4: Non-existent Streamlit Function
```python
st.rerun()  # This doesn't exist in Streamlit
# Should be: st.experimental_rerun() (deprecated)
# Or: st.rerun() (Streamlit 1.27+)
```

## Impact
- **Data loss** - accidental deletions cannot be undone
- **No confirmation** - users may delete wrong patient
- **Compliance risk** - medical data retention requirements
- **Broken UX** - `st.rerun()` may cause errors

## Proposed Remediation

### 1. Add Confirmation Dialog
```python
# Use Streamlit's confirmation dialog (1.22+)
delete_confirmed = st.checkbox("Confirmar eliminación", key=f"confirm_{patient.id}")

if st.button(f"🗑️ Eliminar", key=f"del_{patient.id}", disabled=not delete_confirmed):
    # Safe to delete now
```

Or use a modal pattern:
```python
col1, col2 = st.columns([3, 1])
with col1:
    st.warning(f"¿Eliminar paciente {patient.id[:8]}?")
with col2:
    if st.button("Sí, eliminar", type="danger"):
        delete_patient(patient.id)
```

### 2. Implement Soft Delete
```python
# models/patient.py
class Patient(Base):
    # ... existing fields ...
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String, nullable=True)
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
```

```python
# services/patient_service.py
def soft_delete_patient(self, patient_id: str, deleted_by: str):
    patient = self.db.query(Patient).filter_by(id=patient_id).first()
    patient.deleted_at = datetime.utcnow()
    patient.deleted_by = deleted_by
    self.db.commit()
```

### 3. Fix Technical Bugs
```python
# Fix typo
db = SessionLocal()

# Fix rerun
st.rerun()  # or st.experimental_rerun() for older versions
```

## Labels
`ux`, `bug`, `data-safety`, `medium-priority`, `gdpr`

## Effort Estimate
2-3 hours
