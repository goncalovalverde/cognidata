# Missing Type Hints - Incomplete Type Annotations

## Context
Several methods lack proper type hints, making the code harder to understand and maintain:

```python
# services/audit.py - Missing return types
def get_logs(
    self,
    resource_type: str = None,
    resource_id: str = None,
    action: str = None,
    limit: int = 100,
):
    # Returns: ??? (no return type annotation)
    ...

def get_patient_history(self, patient_id: str, limit: int = 50):
    # Returns: ???
    ...
```

```python
# models/test_session.py - Missing type hints on property accessors
def get_raw_data(self) -> dict:
    return json.loads(self.raw_data) if self.raw_data else {}

def get_calculated_scores(self) -> dict:
    return json.loads(self.calculated_scores) if self.calculated_scores else {}
```

## Impact
- **IDE support suffers** - no autocomplete for return types
- **Harder to understand API** - consumers don't know what to expect
- **Refactoring risk** - changes to return types go undetected
- **Documentation gap** - type hints are documentation

## Proposed Remediation

### Add Complete Type Annotations

```python
# services/audit.py
from typing import List, Optional

def get_logs(
    self,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
) -> List[AuditLog]:
    """Get audit logs with optional filters.
    
    Args:
        resource_type: Filter by resource type (patient, test_session, etc.)
        resource_id: Filter by specific resource ID
        action: Filter by action type (patient.create, test.delete, etc.)
        limit: Maximum number of results to return
    
    Returns:
        List of matching AuditLog entries, ordered by timestamp descending
    """
    ...

def get_patient_history(
    self, 
    patient_id: str, 
    limit: int = 50
) -> List[AuditLog]:
    """Get complete audit history for a patient.
    
    Matches logs where the resource_id starts with patient_id
    OR where details JSON contains the patient_id.
    
    Args:
        patient_id: UUID of the patient
        limit: Maximum number of entries to return
    
    Returns:
        List of audit entries related to this patient
    """
    ...
```

```python
# models/test_session.py
from typing import Dict, Optional

class TestSession(Base):
    # ... existing code ...
    
    def get_raw_data(self) -> Dict:
        """Get the raw test data as a dictionary.
        
        Returns:
            Dictionary containing raw test responses.
            Empty dict if no data stored.
        """
        return json.loads(self.raw_data) if self.raw_data else {}
    
    def get_calculated_scores(self) -> Dict:
        """Get the normative scores calculated from raw data.
        
        Returns:
            Dictionary with keys: puntuacion_escalar, percentil,
            z_score, clasificacion, and norma_aplicada.
            Empty dict if scores not yet calculated.
        """
        return json.loads(self.calculated_scores) if self.calculated_scores else {}
    
    def get_qualitative_data(self) -> Dict:
        """Get qualitative/observational data from the test session.
        
        Returns:
            Dictionary with qualitative observations and checklist items.
            Empty dict if no qualitative data stored.
        """
        return json.loads(self.qualitative_data) if self.qualitative_data else {}
```

## Labels
`type-hints`, `documentation`, `maintainability`, `low-priority`

## Effort Estimate
1 hour
